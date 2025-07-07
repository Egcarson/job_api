from fastapi import FastAPI, status
from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from src.app.auth.utils import create_url_safe_token
from src.db.redis import get_email_verification_token, save_email_verification_token
from src.config import Config
from src.celery_tasks import send_email as celery_worker

class ExceptionSystemManager(Exception):
    """Default home for all API errors"""
    pass

class InvalidToken(ExceptionSystemManager):
    """Invalid token or expired token"""
    pass

class TokenExpired(ExceptionSystemManager):
    """Token expired or user have been logged out"""
    pass

class AccessToken(ExceptionSystemManager):
    """Please provide an access token"""
    pass

class RefreshToken(ExceptionSystemManager):
    """Please provide a refresh token"""
    pass

class RoleCheckAccess(ExceptionSystemManager):
    """You are not allowed to access this endpoint. Action aborted!"""
    pass

class UserAlreadyExists(ExceptionSystemManager):
    """User already exists. Please proceed to Login"""
    pass

class UserNotFound(ExceptionSystemManager):
    """User does not exist!"""
    pass

class InvalidEmailOrPassword(ExceptionSystemManager):
    """Invalid email or password"""
    pass

class InvalidId(ExceptionSystemManager):
    """Invalid ID"""
    pass

class NotAuthorized(ExceptionSystemManager):
    """You are not authorized to access this endpoint."""
    pass

class JobNotFound(ExceptionSystemManager):
    """Job does not exist!"""
    pass

class ApplicationNotFound(ExceptionSystemManager):
    """Application does not exist!"""
    pass

class AccountNotVerified(ExceptionSystemManager):
    """Account has not been verified"""
    def __init__(self, user):
        self.user = user
    

class RoleError(ExceptionSystemManager):
    """Invalid role, please input the correct role"""
    pass

def create_exception_handler(status_code: int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exception: ExceptionSystemManager):

        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )
    
    return exception_handler

def register_all_errors(app: FastAPI):
    #TokenExpired
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid or expired token",
                "resolution": "Please generate a new token or login again",
                "error_code": "invalid_token"
            }
        )
    )
    # TokenExpired
    app.add_exception_handler(
        TokenExpired,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Token has expired or you've been logged out",
                "resolution": "Please generate a new token or login again",
                "error_code": "token_expired"
            }
        )
    )
    # AccessToken
    app.add_exception_handler(
        AccessToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please generate an access token",
                "error_code": "access_token_required"
            }
        )
    )
    # RefreshToken
    app.add_exception_handler(
        RefreshToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get a new refresh token",
                "error_code": "refresh_token_required"
            }
        )
    )
    # RoleCheckAccess
    app.add_exception_handler(
        RoleCheckAccess,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Sorry, you can not proceed!",
                "resolution": "Login as the authorized user to perform this action",
                "error_code": "unauthorized_user_role"
            }
        )
    )
    # UserAlreadyExists
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "User already exists!",
                "resolution": "Signup with a different email or proceed to login",
                "error_code": "user_exists"
            }
        )
    )
    # UserNotFound
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "resolution": "The user does not exist or has been removed",
                "error_code": "user_not_found"
            }
        )
    )
    # InvalidEmailOrPassword
    app.add_exception_handler(
        InvalidEmailOrPassword,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid login credentials",
                "resolution": "Please provide a valid email or password",
                "error_code": "invalid_login_details"
            }
        )
    )
    # InvalidId
    app.add_exception_handler(
        InvalidId,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "This is not a valid UUID number!",
                "resolution": "Please provide a valid id",
                "error_code": "invalid_uid"
            }
        )
    )
    # NotAuthorized
    app.add_exception_handler(
        NotAuthorized,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have the permission to continue!",
                "error_code": "unauthorized_user"
            }
        )
    )
    # JobNotFound
    app.add_exception_handler(
        JobNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Job not found",
                "error_code": "job_not_found"
            }
        )
    )
    # ApplicationNotFound
    app.add_exception_handler(
        ApplicationNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Application not found",
                "error_code": "application_not_found"
            }
        )
    )

    app.add_exception_handler(
        RoleError,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Invalid role, please input the correct role",
                "error_code": "invalid_role",
                "resolution": "role must be 'EMPLOYER', 'USER' or 'ADMIN'"
            }
        )
    )

    # app.add_exception_handler(
    #     AccountNotVerified,
    #     create_exception_handler(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         initial_detail={
    #             "message": "Account not verified",
    #             "error_code": "account_not_verified",
    #             "resolution": "Please check your email for verification link"
    #         }
    #     )
    # )

    #server exception handler
    @app.exception_handler(500)
    async def internal_server_error(request, exc):
        return JSONResponse(
            content={
                "message": "Ooops!............something went wrong",
                "error_code": "server_error"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @app.exception_handler(AccountNotVerified)
    async def account_not_verified_handler(request: Request, exc: AccountNotVerified):
        user = exc.user
        user_email = user.email_address
        existing_token = await get_email_verification_token(user_email)

        if existing_token:
            # Token already in Redis
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": "Account not verified.",
                    "error_code": "account_not_verified",
                    "resolution": "Check your email for the verification link."
                }
            )
        else:
            #No active token, create and send
            new_token = create_url_safe_token({"email": user_email})
            verification_link = f"http://{Config.DOMAIN}/api/v1.0/auth/verify_email/{new_token}"

            html_message = f"""
            <h1>Verify your Email Address</h1>
            <p>Please click on the <a href="{verification_link}">link</a> to verify your account</p>
            """
            subject = "Verify your email"

            # Save the new token
            await save_email_verification_token(user_email, new_token)

            # Send email asynchronously
            celery_worker.delay([user_email], subject, html_message)

            # Respond
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": "Account not verified. A new verification link has been sent.",
                    "error_code": "account_not_verified",
                    "resolution": "Check your email for the new verification link."
                }
            )