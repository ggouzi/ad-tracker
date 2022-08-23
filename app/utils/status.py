from pydantic import BaseModel


class Status(BaseModel):
    detail: str


responses = {
    201: {
            "content": {"application/json": {
                "example": {"detail": "Resouce created"}
            }},
            "model": Status,
            "description": "Return a HTTP 201 on resource creation"
        },
    400: {
            "content": {"application/json": {
                "example": {"detail": "<UI-Friendy & translated error message>"}
            }},
            "model": Status,
            "description": "Return reason why request parsing failed"
        },
    401: {
            "content": {"application/json": {
                "example": {"detail": "Email ou mot de passe incorrect"}
            }},
            "model": Status,
            "description": "Return reason why authentication failed"
        },
    403: {
            "content": {"application/json": {
                "example": {"detail": "Vous n'êtes pas autorisé à effectuer cette action"}
            }},
            "model": Status,
            "description": "Return reason why access is forbidden"
        },
    404: {
            "content": {"application/json": {
                "example": {"detail": "Not found"}
            }},
            "model": Status,
            "description": "Resource was not found"
        },
    409:{
            "content": {"application/json": {
                "example": {"detail": "ProductType already registered"}
            }},
            "model": Status,
            "description": "Return reason what conflict caused request to not be processed"
        },
    413:{
            "content": {"application/json": {
                "example": {"detail": "File is too large"}
            }},
            "model": Status,
            "description": "Returns message saying file cannot be uploaded because it exceeds server maximum allowed size"
        },
    422:{
            "content": {"application/json": {
                "example": {"detail": "No filename type in file object"}
            }},
            "model": Status,
            "description": "Return reason why request cannot be processed"
        },
    500: {
            "content": {"application/json": {
                "example": {"detail": "Internal server error"}
            }},
            "model": Status,
            "description": "Return server error"
        },
    426: {
            "content": {"application/json": {
                "example": {"detail": "Version 0.X not supported", "link": "https://apple.com"}
            }},
            "model": Status,
            "description": "Return message saying version is not supported anymore"
        }
    }


def get_responses(arr):
    result = {}
    for status_code in arr:
        if status_code in responses:
            result[status_code] = responses[status_code]
    return result
