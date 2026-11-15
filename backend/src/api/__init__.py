from fastapi import APIRouter

from api import auth, feedbacks, instructions, progress, steps, users

main_router = APIRouter()

main_router.include_router(users.router)
main_router.include_router(feedbacks.router)
main_router.include_router(instructions.router)
main_router.include_router(progress.router)
main_router.include_router(steps.router)
main_router.include_router(auth.router)
