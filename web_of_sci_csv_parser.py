import csv
import uuid
import re
import os
from pprint import pprint

# ==============================================================================
#  1. INTEGRATED USER-PROVIDED AFFILIATION PARSER
# ==============================================================================
class AffiliationParser:
    """
    This class is a direct implementation of the user's affiliation parsing logic.
    """
    def __init__(self):
        self.countries = self._get_comprehensive_country_list()
        self.business_suffixes = {'ltd', 'inc', 'co', 'llc', 'corp', 'gmbh', 'ag', 'bv', 'srl', 'spa', 'pty'}
        country_pattern_string = r',\s*(' + '|'.join(re.escape(c) for c in self.countries) + r')\b *$'
        self.country_regex = re.compile(country_pattern_string, re.IGNORECASE)
        print("✅ AffiliationParser initialized with user-provided logic.")

    def _get_comprehensive_country_list(self):
        countries = [
            'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia',
            'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium',
            'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Brunei Darussalam',
            'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Central African Republic',
            'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo, Democratic Republic of the',
            'Congo, Republic of the', 'Costa Rica', 'Cote d\'Ivoire', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Czechia',
            'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador',
            'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France', 'French Guiana', 'Gabon',
            'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guam', 'Guatemala', 'Guinea', 'Guinea-Bissau',
            'Guyana', 'Haiti', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland',
            'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kosovo', 'Kuwait',
            'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania',
            'Luxembourg', 'Macao', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands',
            'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro',
            'Morocco', 'Mozambique', 'Myanmar', 'Burma', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand',
            'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Palau',
            'Palestine', 'State of Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal',
            'Puerto Rico', 'Qatar', 'Romania', 'Russia', 'Russian Federation', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia',
            'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia',
            'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands',
            'Somalia', 'South Africa', 'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname',
            'Sweden', 'Switzerland', 'Syria', 'Syrian Arab Republic', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste',
            'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkiye', 'Turkmenistan', 'Tuvalu', 'Uganda',
            'Ukraine', 'United Arab Emirates', 'U Arab Emirates', 'UAE', 'United Kingdom', 'UK', 'United States of America', 'United States', 'USA',
            'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City', 'Venezuela', 'Viet Nam', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe',
            'Peoples R China', 'England', 'Scotland', 'Wales', 'Northern Ireland', 'North Ireland'
        ]
        countries.sort(key=len, reverse=True)
        return countries

    def parse(self, affiliation_text):
        country, city, institution = '', '', ''
        work_string = affiliation_text.strip()
        
        # First, check for country at the end
        country_match = self.country_regex.search(work_string)
        if country_match:
            country = country_match.group(1).strip()
            # Normalize country names
            if country.lower() == 'turkiye':
                country = 'Turkey'
            elif country.lower() == 'north ireland':
                country = 'Northern Ireland'
            elif country.lower() in ['u arab emirates', 'uae']:
                country = 'United Arab Emirates'
            work_string = work_string[:country_match.start()].strip()
        
        parts = [part.strip() for part in work_string.split(',') if part.strip()]
        
        # Handle US state code with zip (e.g., "GA 30332", "TX 78712")
        if len(parts) > 0:
            last_part = parts[-1]
            # Check if last part matches pattern: STATE_CODE ZIP (e.g., "GA 30332", "TX USA")
            us_pattern = re.match(r'^([A-Z]{2})\s+(?:\d{5})?.*$', last_part)
            if us_pattern and not country:
                # This is a US state code, extract it as city and set country to USA
                city = us_pattern.group(1)  # Use state code as city identifier
                country = 'United States'
                parts.pop(-1)
                institution = ', '.join(parts) if parts else 'Unknown'
            else:
                # Normal processing
                if len(parts) > 1:
                    potential_city = parts[-1]
                    cleaned_suffix_check = re.sub(r'[^a-zA-Z]', '', potential_city).lower()
                    if cleaned_suffix_check in self.business_suffixes:
                        institution = ', '.join(parts)
                        city = ''
                    else:
                        city = parts.pop(-1)
                        institution = ', '.join(parts)
                elif len(parts) == 1:
                    institution = parts[0]
                else:
                    institution = work_string
        
        return {"institution_name": institution or "Unknown", "city": city or "Unknown", "country": country or "Unknown"}


# ==============================================================================
#  2. WEB OF SCIENCE DATA PARSER
# ==============================================================================
class WebOfScienceParser:
    """
    Reads a Web of Science CSV, validates its columns, and transforms the data
    into a clean, structured format ready for ingestion.
    """
    REQUIRED_COLUMNS = [
        'Article Title', 'Author Full Names', 'Addresses', 'Author Keywords',
        'Source Title', 'Publication Year', 'UT (Unique WOS ID)'
    ]
    
    def __init__(self):
        self.affiliation_parser = AffiliationParser()
        self._venues = {}
        self._authors = {}
        self._keywords = {}
        self._affiliations = {}
        # Document type mapping
        self.document_type_mapping = {
            'J': 'Journal',
            'B': 'Book',
            'S': 'Series',
            'P': 'Patent',
            'C': 'Conference'
        }

    def _validate_columns(self, fieldnames):
        """Checks if all required columns are present in the CSV header."""
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in fieldnames]
        if missing_cols:
            raise ValueError(f"CSV file is missing required columns: {', '.join(missing_cols)}")
        print("✅ Column validation passed.")

    def _get_or_create_entity(self, store, key, factory):
        """Generic helper to find or create an entity."""
        if key not in store:
            store[key] = factory()
        return store[key]

    def parse_file(self, filepath):
        """Main method to parse the Web of Science CSV file."""
        print(f"🚀 Starting parsing for: {filepath}")
        
        processed_data = {
            "records": [], "authors": [], "venues": [], "keywords": [],
            "affiliations": [], "record_authors": [], "record_keywords": []
        }

        with open(filepath, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            self._validate_columns(reader.fieldnames)
            
            for row in reader:
                # --- Create Author ID Mapping for the current row ---
                # WoS provides author names and IDs in the same order in separate columns.
                author_names = [name.strip() for name in row.get('Author Full Names', '').split(';')]
                researcher_ids = [rid.strip() for rid in row.get('Researcher Ids', '').split(';')]
                orcids = [oid.strip() for oid in row.get('ORCIDs', '').split(';')]
                
                author_details_map = {}
                for i, name in enumerate(author_names):
                    # Extract the ID part from "Name, First/ID" format for both Researcher ID and ORCID
                    rid_match = re.search(r'/(.*)$', researcher_ids[i]) if i < len(researcher_ids) else None
                    orcid_match = re.search(r'/(.*)$', orcids[i]) if i < len(orcids) and orcids[i] else None
                    author_details_map[name] = {
                        "researcher_id": rid_match.group(1) if rid_match else None,
                        "orcid": orcid_match.group(1) if orcid_match else None
                    }

                # --- Process Venue ---
                issn = row.get('ISSN', '').strip()
                venue_key = issn if issn else row.get('Source Title', 'Unknown').strip().lower()
                venue = self._get_or_create_entity(self._venues, venue_key, lambda: {
                    "venue_id": str(uuid.uuid4()),
                    "venue_name": row.get('Source Title', '').strip(), "issn": issn
                })

                # --- Process Record ---
                record_id = str(uuid.uuid4())
                
                # Map publication type code to full name
                pub_type_code = row.get('Publication Type', '').strip()
                document_type = self.document_type_mapping.get(pub_type_code, pub_type_code)
                
                processed_data["records"].append({
                    "record_id": record_id, 
                    "title": row.get('Article Title', '').strip(),
                    "document_type": document_type,
                    "year": row.get('Publication Year'), 
                    "doi": row.get('DOI'),
                    "wos_ut": row.get('UT (Unique WOS ID)'), 
                    "venue_id": venue["venue_id"]
                })
                
                # --- Process and Link Keywords (Using Author Keywords only, per prior request) ---
                keywords_str = row.get('Author Keywords', '')
                if keywords_str:
                    for kw_text in keywords_str.split(';'):
                        normalized_kw = kw_text.strip().lower()
                        if normalized_kw:
                            keyword = self._get_or_create_entity(self._keywords, normalized_kw, lambda: {
                                "keyword_id": str(uuid.uuid4()), "keyword": normalized_kw
                            })
                            processed_data["record_keywords"].append({"record_id": record_id, "keyword_id": keyword["keyword_id"]})

                # --- Process and Link Authors & Affiliations from 'Addresses' column ---
                addresses_str = row.get('Addresses', '')
                # Regex to find "[Author list] Affiliation" patterns
                address_matches = re.findall(r'\[(.*?)\]\s*(.*?)(?=\s*\[|$)', addresses_str)
                for match in address_matches:
                    author_list_str, affil_text = match
                    
                    # Clean affiliation text: strip whitespace and trailing semicolons
                    affil_text = affil_text.strip().rstrip(';').strip()
                    
                    # Get Affiliation
                    normalized_affil = affil_text.lower()
                    affiliation = self._get_or_create_entity(self._affiliations, normalized_affil, lambda: {
                        "affiliation_id": str(uuid.uuid4()),
                        **self.affiliation_parser.parse(affil_text)
                    })

                    # Link all authors in the list to this affiliation
                    for author_name in author_list_str.split('; '):
                        details = author_details_map.get(author_name)
                        if not details: continue

                        # Parse author name into first and last name (format: "Last Name, First Name")
                        name_parts = author_name.split(',', 1)
                        last_name = name_parts[0].strip() if len(name_parts) > 0 else author_name
                        first_name = name_parts[1].strip() if len(name_parts) > 1 else ""

                        # Use Researcher ID as the primary key for deduplication
                        author_key = details["researcher_id"] or details["orcid"] or author_name.lower()
                        author = self._get_or_create_entity(self._authors, author_key, lambda: {
                            "author_id": str(uuid.uuid4()), 
                            "first_name": first_name,
                            "last_name": last_name,
                            "wos_researcher_id": details["researcher_id"], 
                            "orcid": details["orcid"]
                        })
                        processed_data["record_authors"].append({
                            "record_id": record_id, "author_id": author["author_id"],
                            "affiliation_id": affiliation["affiliation_id"]
                        })

        # Finalize the data by converting helper dicts to lists
        processed_data['authors'] = list(self._authors.values())
        processed_data['venues'] = list(self._venues.values())
        processed_data['keywords'] = list(self._keywords.values())
        processed_data['affiliations'] = list(self._affiliations.values())
        print("✅ Parsing complete!")
        return processed_data


# ==============================================================================
#  3. EXPORT DATA TO CSV FILES
# ==============================================================================
def export_data_to_csv(data, output_dir='output_csvs_wos'):
    print(f"\n🚀 Exporting data to CSV files in '{output_dir}/' directory...")
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    for table_name, table_data in data.items():
        if not table_data:
            print(f"  -> Skipping '{table_name}.csv' (no data).")
            continue
        file_path = os.path.join(output_dir, f"{table_name}.csv")
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=table_data[0].keys())
                writer.writeheader()
                writer.writerows(table_data)
            print(f"  -> Successfully wrote {len(table_data)} rows to '{file_path}'")
        except IOError as e: print(f"  -> ERROR writing to '{file_path}': {e}")
    print("\n✅ CSV export complete!")


# ==============================================================================
#  4. MAIN EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    wos_csv_path = 'fwos_BIM_random_1000.csv'
    
    try:
        parser = WebOfScienceParser()
        clean_data = parser.parse_file(wos_csv_path)
        export_data_to_csv(clean_data)

    except FileNotFoundError:
        print(f"ERROR: The file was not found at '{wos_csv_path}'")
    except ValueError as e:
        print(f"ERROR: A validation error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")