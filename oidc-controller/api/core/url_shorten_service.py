import logging
from uuid import UUID

from ..db.models import ShortenedURL

logger = logging.getLogger(__name__)

controller_host = "https://1d7e-165-225-211-70.ngrok.io"


async def resolve_url(id: UUID):
    logger.debug(">>> resolve_url")
    record: ShortenedURL = await ShortenedURL.find_by_id(id)
    # await record.delete()
    return record.url


async def create_url(url) -> UUID:
    logger.debug(">>> create_url")
    short_url = ShortenedURL(url=url)
    await short_url.save()

    return controller_host + "/url/" + str(short_url.id)
