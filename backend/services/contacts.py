from pipecat.services.llm_service import FunctionCallParams
from loguru import logger
import json


# all available/known names in the contact book to map to information in the contact book
known_names = {
    "Javier Friedman": "a1",
    "Javier": "a1",
    "Javi": "a1",
    "Bronn": "a2",
    "Bron": "a2",
    "Sam Bronstein": "a2",
    "Sam": "a2",
    "tony stark": "a3",
    "Tony": "a3",
}   

contact_book = {
    "a1": {
        "email": "javier.friedman@tufts.edu",
        "phone": "+191754480541",
        "address": "123 Main St, Anytown, USA"
    },
    "a2": {
        "email": "sam.bronstein@example.com",
        "phone": "456-789-0123",
        "address": "456 Main St, Anytown, USA"
    },
    "a3": {
        "email": "tony.stark@example.com",
        "phone": "789-012-3456",
        "address": "789 Main St, Anytown, USA"
    }

}

async def fetch_all_known_contacts(params: FunctionCallParams):
    """Fetch all known contacts from the contact book."""
    logger.info(f"🛠 TOOL CALL: fetch_all_known_contacts() invoked")
    known_contacts = {name for name in known_names.keys()}
    await params.result_callback(json.dumps(known_contacts, indent=2))
    return json.dumps(known_contacts, indent=2)

async def get_contact_information(params: FunctionCallParams):
    """JAVIS' contact book. Get a person contact information
        if user wants to send an email or a text check to see if the person
        is in the contact book.

    Expected arguments from the LLM (passed via params.arguments):
        name:      Person's name
    """
    
    name = params.arguments.get("name", "")
    logger.info(f"🛠 TOOL CALL: get_contact_information() invoked — name={name}")
    if name not in known_names:
        await params.result_callback("Person name not found in contact book.")  
        return
    else:
        await params.result_callback(f"Contact information for {name}: {contact_book[known_names[name]]}")
        return f"Contact information for {name}: {contact_book[known_names[name]]}"
