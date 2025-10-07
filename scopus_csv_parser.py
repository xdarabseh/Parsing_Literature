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
#  2. INTEGRATED USER-PROVIDED AUTHOR PARSER
# ==============================================================================
class AuthorParser:
    """
    This class is a direct implementation of the user's author parsing logic.
    """
    def __init__(self):
        self.author_pattern = re.compile(r'([^,]+),\s(.*?)\s\((\d+)\)')
        print("✅ AuthorParser initialized with user-provided logic.")

    def parse(self, author_full_name_entry):
        """
        Parses a single author entry string from the 'Author full names' column.
        """
        match = self.author_pattern.search(author_full_name_entry.strip())
        if match:
            last_name, first_name, author_id = match.groups()
            return {
                'first_name': first_name.strip(),
                'last_name': last_name.strip(),
                'scopus_author_id': author_id.strip()
            }
        return None

# ==============================================================================
#  3. MAIN SCOPUS DATA PARSER
# ==============================================================================
class ScopusParser:
    REQUIRED_COLUMNS = ['Title', 'Author full names', 'Authors with affiliations', 'Affiliations', 'Source title', 'Author Keywords', 'Abstract', 'Document Type', 'Year', 'DOI', 'EID']
    
    def __init__(self):
        self.affiliation_parser = AffiliationParser()
        self.author_parser = AuthorParser()
        self._venues, self._authors, self._keywords, self._affiliations = {}, {}, {}, {}

    def _validate_columns(self, fieldnames):
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in fieldnames]
        if missing_cols:
            raise ValueError(f"CSV file is missing required columns: {', '.join(missing_cols)}")
        print("✅ Column validation passed.")

    def _get_or_create_entity(self, store, key, factory):
        if key and key not in store: store[key] = factory()
        return store.get(key)

    def parse_file(self, filepath):
        print(f"🚀 Starting parsing for: {filepath}")
        processed_data = {"records": [], "authors": [], "venues": [], "keywords": [], "affiliations": [], "record_authors": [], "record_keywords": []}

        with open(filepath, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            self._validate_columns(reader.fieldnames)
            
            for row in reader:
                record_id = str(uuid.uuid4())
                
                issn = row.get('ISSN', '').strip()
                venue = self._get_or_create_entity(self._venues, issn if issn else row.get('Source title', 'Unknown').strip().lower(), lambda: {"venue_id": str(uuid.uuid4()), "venue_name": row.get('Source title', '').strip(), "venue_type": "Journal", "issn": issn})
                processed_data["records"].append({"record_id": record_id, "title": row.get('Title', '').strip(), "abstract": row.get('Abstract', '').strip(), "document_type": row.get('Document Type', '').strip(), "publication_year": int(row['Year']) if row.get('Year', '').isdigit() else None, "doi": row.get('DOI'), "eid": row.get('EID'), "venue_id": venue["venue_id"] if venue else None})
                
                if row.get('Author Keywords'):
                    for kw in row['Author Keywords'].split(';'):
                        norm_kw = kw.strip().lower()
                        if norm_kw:
                            keyword = self._get_or_create_entity(self._keywords, norm_kw, lambda: {"keyword_id": str(uuid.uuid4()), "keyword": norm_kw})
                            processed_data["record_keywords"].append({"record_id": record_id, "keyword_id": keyword["keyword_id"]})

                # --- NEW PARSING STRATEGY BASED ON USER LOGIC ---
                
                # Build affiliation map: author name -> affiliation text
                affiliation_map = {}
                if row.get('Authors with affiliations'):
                    for entry in row['Authors with affiliations'].split(';'):
                        entry = entry.strip()
                        # Format: "Last Name, First Name, affiliation details"
                        # We need to extract the author name (first two parts) and affiliation (rest)
                        parts = [p.strip() for p in entry.split(',')]
                        if len(parts) >= 3:
                            # First two parts are name (Last, First), rest is affiliation
                            author_name = f"{parts[0]}, {parts[1]}"
                            affil_text = ', '.join(parts[2:])
                            affiliation_map[author_name.strip()] = affil_text.strip()
                
                author_full_names_str = row.get('Author full names', '')
                if isinstance(author_full_names_str, str):
                    for author_entry in author_full_names_str.split(';'):
                        parsed_author = self.author_parser.parse(author_entry)
                        if parsed_author:
                            scopus_id = parsed_author['scopus_author_id']
                            author = self._get_or_create_entity(self._authors, scopus_id, lambda: {"author_id": str(uuid.uuid4()), **parsed_author})
                            
                            affiliation = None
                            # Try to match author by "Last Name, First Name" format
                            author_key = f"{parsed_author['last_name']}, {parsed_author['first_name']}"
                            affil_text = affiliation_map.get(author_key)
                            if affil_text:
                                norm_affil = affil_text.lower()
                                affiliation = self._get_or_create_entity(self._affiliations, norm_affil, lambda: {"affiliation_id": str(uuid.uuid4()), **self.affiliation_parser.parse(affil_text)})
                            
                            processed_data["record_authors"].append({"record_id": record_id, "author_id": author["author_id"], "affiliation_id": affiliation["affiliation_id"] if affiliation else None})

        processed_data['authors'] = list(self._authors.values())
        processed_data['venues'] = list(self._venues.values())
        processed_data['keywords'] = list(self._keywords.values())
        processed_data['affiliations'] = list(self._affiliations.values())
        print("✅ Parsing complete!")
        return processed_data

# ==============================================================================
#  4. EXPORT DATA TO CSV FILES
# ==============================================================================
def export_data_to_csv(data, output_dir='output_csvs_scopus'):
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
#  5. MAIN EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    scopus_csv_path = 'scopus.csv'
    try:
        parser = ScopusParser()
        clean_data = parser.parse_file(scopus_csv_path)
        export_data_to_csv(clean_data)
    except FileNotFoundError:
        print(f"ERROR: The file was not found at '{scopus_csv_path}'")
    except ValueError as e:
        print(f"ERROR: A validation error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")