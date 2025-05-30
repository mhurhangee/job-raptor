from jobspy import scrape_jobs
import pandas as pd
from re import sub

def get_user_input(prompt, default=None):
    """Get user input with an optional default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ")
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ")

def get_boolean_input(prompt, default=False):
    """Get a yes/no response from the user."""
    default_text = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_text}]: ").strip().lower()
    
    if not response:  # User pressed Enter
        return default
    
    return response.startswith('y')

def print_header(header: str):
    print("\n===== " + header + " =====\n")

def print_item(item: str):
    print("> " + item)

def print_warning(item: str):
    print("\n!!! " + item + "!!!\n")

def clean_description(description):
    """Clean job description by removing excessive whitespace and line breaks."""
    if not description:
        return ""
    
    # Replace multiple newlines with a single one

    cleaned = sub(r'\n+', '\n', description)
    # Replace multiple spaces with a single one
    cleaned = sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def display_job_details(job):
    """Display non-empty fields of a job listing."""
    print("\n" + "=" * 50)
    
    # Get all attributes that have values
    for col in job._fields:
        if col == 'Index':  # Skip the index
            continue
            
        value = getattr(job, col)
        
        # Skip empty values
        if value is None or (isinstance(value, str) and not value.strip()) or value == 'None':
            continue
            
        # Handle description separately
        if col == 'description':
            cleaned_desc = clean_description(value)
            # Show only first 200 characters of description
            if len(cleaned_desc) > 200:
                print(f"\n{col.capitalize()}: {cleaned_desc[:200]}...")
            else:
                print(f"\n{col.capitalize()}: {cleaned_desc}")
        else:
            print(f"{col.capitalize()}: {value}")
    
    print("=" * 50)

def job_search():
    """Collect job search parameters from the user in a form-like interface."""
    print_header("JobRaptor LinkedIn Search Form")
    # Collect search parameters
    search_term = get_user_input("> Search term?", "ai engineer")
    location = get_user_input("> Location?", "UK")
    is_remote = get_boolean_input("> Remote only?", True)
    results_wanted = int(get_user_input("> Number of results?", "100"))
    hours_old = int(get_user_input("> How many hours old (max)?", "24"))
    
    # Confirm search parameters
    print_header("Search Parameters")
    print_item("Search term: " + search_term)
    print_item("Site:        LinkedIn")
    print_item("Location:    " + location)
    print_item("Remote only: " + ("Yes" if is_remote else "No"))
    print_item("Num results: " + str(results_wanted))
    print_item("Hours old:   " + str(hours_old))
    
    # Ask for confirmation
    if not get_boolean_input("\nProceed with search?", True):
        print_warning("Search canceled")
        return

    print("\nSearching for jobs on LinkedIn with parameters: " + str(search_term) + ", " + str(location) + ", " + str(is_remote) + ", " + str(results_wanted) + ", " + str(hours_old) + "... (this may take a moment)")

    try:
        # Perform search
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=search_term,
            results_wanted=results_wanted,
            hours_old=hours_old,
            is_remote=is_remote,
            location=location,
            linkedin_fetch_description=True,
        )
        
        # Check if search was successful
        if isinstance(jobs, pd.DataFrame) and not jobs.empty:
            print_item(f"Found {len(jobs)} jobs")

             # Ask if user wants to review jobs
            if get_boolean_input("\nWould you like to review the jobs?", True):
                # Create a new DataFrame to store kept jobs
                kept_jobs = pd.DataFrame(columns=jobs.columns)
                
                # Review each job one by one
                for i, job in enumerate(jobs.itertuples(), 1):
                    print(f"\nReviewing Job {i} of {len(jobs)}:")
                    display_job_details(job)
                    
                    # Ask if user wants to keep this job
                    if get_boolean_input("Keep this job?", True):
                        # Add to kept jobs DataFrame
                        kept_jobs = pd.concat([kept_jobs, jobs.iloc[[job.Index]]], ignore_index=True)
                        print("Job saved.")
                    else:
                        print("Job discarded.")
                
                # Show summary of kept jobs
                print(f"\nYou kept {len(kept_jobs)} out of {len(jobs)} jobs.")
                
                # If user kept any jobs, ask if they want to save them
                if not kept_jobs.empty and get_boolean_input("\nSave kept jobs to CSV?", True):
                    today = pd.Timestamp.now().strftime('%Y%m%d')
                    clean_search_term = search_term.lower().replace(' ', '_')
                    default_filename = f"{today}-{clean_search_term}.csv"
                    filename = get_user_input("Filename", default_filename)
                    kept_jobs.to_csv(filename, index=False)
                    print(f"Kept jobs saved to {filename}")

        else:
            print_warning("No jobs found")
    except Exception as e:
        print_warning("Search failed: " + str(e))
        return

    # Display results
    print_header("Search Results")
    for job in jobs:
        print_item(job)

def main():
    print_header("Welcome to JobRaptor")
    print("Your AI-powered job search assistant!")

    while True:
        print_header("JobRaptor Menu")
        print("1. Search for jobs")
        print("2. Exit")
            
        choice = input("\nEnter your choice (1-2): ")
            
        if choice == '1':
            job_search()
        elif choice == '2':
            print_header("Thank you for using JobRaptor!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 
