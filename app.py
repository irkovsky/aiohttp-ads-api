import asyncio
from aiohttp import web, BasicAuth
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from models import Base, engine, async_session, User, Ad
from schema import CreateUser, CreateAd, UpdateAd, validate
from errors import HttpError, error_middleware


async def get_ad(session, ad_id):
    ad = await session.get(Ad, ad_id)
    if ad is None:
        raise HttpError(404, "ad not found")
    return ad


async def get_current_user(session, request: web.Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HttpError(401, "authorization required")

    try:
        # Парсим заголовок "Basic base64(email:password)"
        auth = BasicAuth.decode(auth_header)
    except Exception:
        raise HttpError(401, "invalid auth header")

    stmt = select(User).where(User.email==auth.login) 
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None or not user.check_password(auth.password):
        raise HttpError(401, "invalid credentials")
    
    return user

async def create_user(request: web.Request) -> web.Response:
    json_data = await request.json()
    data = validate(CreateUser, json_data)
    
    async with async_session() as session:
        user = User(email=data["email"])
        user.set_password(data["password"])
        session.add(user)
        await session.commit()
        return web.json_response(user.to_dict(), status=201)


async def create_ad(request: web.Request) -> web.Response:
    json_data = await request.json()
    data = validate(CreateAd, json_data)

    async with async_session() as session:
        user = await get_current_user(session, request)
        ad = Ad(**data, owner_id=user.id)
        session.add(ad)
        await session.commit()
        return web.json_response(ad.to_dict(), status=201)


async def get_ad_view(request: web.Request) -> web.Response:
    ad_id = int(request.match_info['ad_id'])
    async with async_session() as session:
        ad = await get_ad(session, ad_id)
        return web.json_response(ad.to_dict())


async def patch_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info['ad_id'])
    json_data = await request.json()
    data = validate(UpdateAd, json_data)

    async with async_session() as session:
        user = await get_current_user(session, request)
        ad = await get_ad(session, ad_id)
        if ad.owner_id != user.id:
            raise HttpError(403, "access denied")
        for field, value in data.items():
            setattr(ad, field, value)
        await session.commit()
        return web.json_response(ad.to_dict())


async def delete_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info['ad_id'])
    async with async_session() as session:
        user = await get_current_user(session, request)
        ad = await get_ad(session, ad_id)
        if ad.owner_id != user.id:
            raise HttpError(403, "access denied")
        await session.delete(ad)
        await session.commit()
        return web.json_response({"status": "deleted"})
    
    
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = web.Application(middlewares=[error_middleware])

app.on_startup.append(init_db)

app.router.add_post('/users', create_user)
app.router.add_post('/ads', create_ad)
app.router.add_get('/ads/{ad_id}', get_ad_view)
app.router.add_patch('/ads/{ad_id}', patch_ad)
app.router.add_delete('/ads/{ad_id}', delete_ad)
        

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)