# contacts.py
import json
import subprocess
from utils import clean_name, fuzzy_match

def get_contacts():
    """Fetch contacts using termux-contact-list and return list with cleaned names, phones, emails."""
    try:
        result = subprocess.run(["termux-contact-list"], capture_output=True, text=True, check=True)
        contacts_json = json.loads(result.stdout)
        contacts = []
        for c in contacts_json:
            name = c.get('name', '')
            clean = clean_name(name)
            if not clean:
                continue

            # Try to get phone number from various possible fields
            phone = None
            if 'phoneNumbers' in c and c['phoneNumbers']:
                phone = c['phoneNumbers'][0].get('number')
            elif 'number' in c:
                phone = c['number']
            
            # Try to get email
            email = None
            if 'emails' in c and c['emails']:
                email = c['emails'][0].get('address')
            elif 'email' in c:
                email = c['email']

            if phone or email:
                contacts.append({
                    'original_name': name,
                    'clean_name': clean.lower(),
                    'phone': phone,
                    'email': email
                })
        # Debug: uncomment to see loaded contacts
        # print("Loaded contacts:", [(c['original_name'], c['phone']) for c in contacts])
        return contacts
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return []

def match_contact(query):
    """
    Find the best matching contact for a given query (case‑insensitive, fuzzy).
    Returns (contact_dict, score) or (None, 0) if no good match.
    """
    contacts = get_contacts()
    if not contacts:
        return None, 0

    query_lower = query.lower()
    best_match = None
    best_score = 0

    for c in contacts:
        # Exact substring match
        if query_lower in c['clean_name']:
            score = 1.0
            if best_score < score:
                best_score = score
                best_match = c
                continue

        # Fuzzy match
        ratio = fuzzy_match(query_lower, c['clean_name'])
        if ratio > best_score:
            best_score = ratio
            best_match = c

    # Debug: uncomment to see match scores
    # print(f"Best match for '{query}': {best_match['original_name'] if best_match else None} with score {best_score}")

    # Lowered threshold to 0.5 for better recall
    if best_score > 0.5:
        return best_match, best_score
    return None, 0
