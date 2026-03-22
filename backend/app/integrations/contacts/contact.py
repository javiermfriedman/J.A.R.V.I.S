from pipecat.services.llm_service import FunctionCallParams
from .contact_book import known_names, contact_book
from loguru import logger
import json


async def fetch_all_known_contacts(params: FunctionCallParams):
    """Fetch all known contacts from the contact book."""
    logger.info(f"🛠 TOOL CALL: fetch_all_known_contacts() invoked")
    known_contacts = {name for name in known_names.keys()}
    await params.result_callback(json.dumps(known_contacts, indent=2))
    return json.dumps(known_contacts, indent=2)

async def get_contact_information(params: FunctionCallParams):
    """Look up contact details by name from the contact book."""
    name = params.arguments.get("name", "")
    logger.info(f"🛠 TOOL CALL: get_contact_information() invoked — name={name}")
    if name not in known_names:
        await params.result_callback("Person name not found in contact book.")
        return

    info = f"Contact information for {name}: {contact_book[known_names[name]]}"
    await params.result_callback(info)
    return info
