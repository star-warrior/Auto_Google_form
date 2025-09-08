import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

form_link = "https://docs.google.com/forms/d/e/1FAIpQLSfW8n4SA_az3og8CNN6YQYOxWRRXtA9eq6A5Py9W9u3hX7f0g/viewform"

# Configuration
AUTO_SUBMIT = True  # Set to False if you want to review the form before submitting manually
COOLDOWN_SECONDS = 20  # Wait time between form submissions
CSV_FILE_PATH = "./form_data.csv"  # Path to CSV file containing form data

def read_data_from_csv():
    """Read form data from CSV file"""
    try:
        if not os.path.exists(CSV_FILE_PATH):
            print(f"❌ CSV file not found: {CSV_FILE_PATH}")
            print("📝 Please create a CSV file with the following columns:")
            print("   - partner_email")
            print("   - student_email") 
            print("   - date")
            print("   - flow_status (Yes/No/Not sure)")
            print("   - file_path (optional - path to file to upload)")
            return None
        
        # Read CSV file
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Convert to list of dictionaries
        data_list = df.to_dict('records')
        
        # Clean up NaN values and empty strings
        for entry in data_list:
            for key, value in entry.items():
                if pd.isna(value):
                    entry[key] = ""
        
        print(f"📊 Loaded {len(data_list)} entries from CSV file")
        return data_list
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return None

def ensure_test_file_exists():
    """Create a test file for upload if it doesn't exist"""
    test_file = "./test_upload.txt"
    if not os.path.exists(test_file):
        with open(test_file, 'w') as f:
            f.write("Test file for Google Form upload\nCreated automatically by autoFormer script\n")
        print(f"📄 Created test file: {os.path.abspath(test_file)}")
    return test_file

def fill_form_generic(browser, person):
    """Form filler specifically designed for your Google Form"""
    print("🔍 Looking for form fields...")
    
    # 1. Partner Email - First text input with specific aria-labelledby
    try:
        partner_email_input = browser.find_element(By.CSS_SELECTOR, "input[aria-labelledby='i1 i4']")
        if partner_email_input.is_displayed() and partner_email_input.is_enabled():
            partner_email_input.clear()
            partner_email_input.send_keys(person["partner_email"])
            print(f"✅ Filled Partner Email: {person['partner_email']}")
        else:
            print("⚠️  Partner email field not interactable")
    except Exception as e:
        print(f"❌ Could not fill partner email: {str(e)[:50]}...")
    
    # 2. Student Email - Second text input with specific aria-labelledby
    try:
        student_email_input = browser.find_element(By.CSS_SELECTOR, "input[aria-labelledby='i6 i9']")
        if student_email_input.is_displayed() and student_email_input.is_enabled():
            student_email_input.clear()
            student_email_input.send_keys(person["student_email"])
            print(f"✅ Filled Student Email: {person['student_email']}")
        else:
            print("⚠️  Student email field not interactable")
    except Exception as e:
        print(f"❌ Could not fill student email: {str(e)[:50]}...")
    
    # 3. Date field - Specific date input
    try:
        date_input = browser.find_element(By.CSS_SELECTOR, "input[type='date'][aria-labelledby='i16']")
        if date_input.is_displayed() and date_input.is_enabled():
            date_input.clear()
            date_input.send_keys(person["date"])
            print(f"✅ Filled Date: {person['date']}")
        else:
            print("⚠️  Date field not interactable")
    except Exception as e:
        print(f"❌ Could not fill date: {str(e)[:50]}...")
    
    # 4. Radio Button Selection - "Did the student complete the full flow?"
    try:
        # Find the radio button based on the data-value attribute
        target_value = person["flow_status"]  # "Yes", "No", or "Not sure"
        radio_button = browser.find_element(By.CSS_SELECTOR, f"div[data-value='{target_value}'][role='radio']")
        
        if radio_button.is_displayed() and radio_button.is_enabled():
            radio_button.click()
            print(f"✅ Selected radio option: {target_value}")
        else:
            print(f"⚠️  Radio button '{target_value}' not interactable")
    except Exception as e:
        print(f"❌ Could not select radio option: {str(e)[:50]}...")
    
    # 5. File Upload - Optional screenshots/evidence
    try:
        if person.get("file_path") and person["file_path"].strip():
            file_path = os.path.abspath(person["file_path"])
            
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                print("💡 Skipping file upload since file doesn't exist")
            else:
                print(f"🔍 Attempting to upload file: {file_path}")
                
                # First, try to click the upload button to open the Google Drive picker
                upload_selectors = [
                    "div[jsname='mWZCyf'][aria-label='Add file']",
                    "div[aria-label='Add file']",
                    ".uArJ5e.cd29Sd",  # Classes from your HTML
                    "div[role='button']:contains('Add file')"
                ]
                
                upload_clicked = False
                for selector in upload_selectors:
                    try:
                        upload_button = browser.find_element(By.CSS_SELECTOR, selector)
                        if upload_button.is_displayed():
                            print(f"📎 Found upload button, clicking it...")
                            upload_button.click()
                            time.sleep(3)  # Wait for Google Drive picker to load
                            upload_clicked = True
                            break
                    except Exception:
                        continue
                
                if upload_clicked:
                    # Look for the Google Drive picker dialog
                    try:
                        picker_dialog = browser.find_element(By.CSS_SELECTOR, ".picker-dialog")
                        if picker_dialog.is_displayed():
                            print("📁 Google Drive picker opened successfully!")
                            
                            # Switch to the iframe containing the file picker
                            iframe = browser.find_element(By.CSS_SELECTOR, ".picker-dialog iframe")
                            browser.switch_to.frame(iframe)
                            
                            # Look for the upload tab/button in the picker
                            time.sleep(2)
                            upload_tab_selectors = [
                                "div[data-id='upload']",
                                "div:contains('Upload')",
                                ".picker-upload-button",
                                "[aria-label*='Upload']"
                            ]
                            
                            tab_clicked = False
                            for tab_selector in upload_tab_selectors:
                                try:
                                    upload_tab = browser.find_element(By.CSS_SELECTOR, tab_selector)
                                    if upload_tab.is_displayed():
                                        upload_tab.click()
                                        time.sleep(2)
                                        tab_clicked = True
                                        print("📤 Clicked upload tab in picker")
                                        break
                                except:
                                    continue
                            
                            # Now look for the file input in the picker
                            file_inputs = browser.find_elements(By.CSS_SELECTOR, "input[type='file']")
                            if file_inputs:
                                file_inputs[0].send_keys(file_path)
                                print(f"✅ File uploaded to Google Drive picker: {file_path}")
                                time.sleep(3)  # Wait for upload to process
                                
                                # Look for and click the "Insert" or "Select" button
                                insert_selectors = [
                                    "button:contains('Insert')",
                                    "button:contains('Select')",
                                    "div[role='button']:contains('Insert')",
                                    ".picker-insert-button"
                                ]
                                
                                for insert_selector in insert_selectors:
                                    try:
                                        insert_button = browser.find_element(By.CSS_SELECTOR, insert_selector)
                                        if insert_button.is_displayed():
                                            insert_button.click()
                                            print("✅ Clicked Insert button")
                                            break
                                    except:
                                        continue
                            else:
                                print("❌ Could not find file input in Google Drive picker")
                            
                            # Switch back to main frame
                            browser.switch_to.default_content()
                            time.sleep(2)
                            
                        else:
                            print("❌ Google Drive picker dialog not visible")
                    except Exception as picker_e:
                        print(f"❌ Error with Google Drive picker: {str(picker_e)[:50]}...")
                        browser.switch_to.default_content()  # Make sure we're back to main frame
                else:
                    print("❌ Could not find or click upload button")
                    print("💡 Manual file upload may be required")
    except Exception as e:
        print(f"❌ Could not upload file: {str(e)[:50]}...")
        # Ensure we're back to main frame if something went wrong
        try:
            browser.switch_to.default_content()
        except:
            pass
    
    print("\n🎯 Form filling completed!")
    
    # 6. Automatic Form Submission (if enabled)
    if AUTO_SUBMIT:
        try:
            print("🚀 Looking for Submit button...")
            
            # Try multiple selectors for the submit button based on your HTML
            submit_selectors = [
                "div[jsname='M2UYVd'][aria-label='Submit']",  # Most specific from your HTML
                "div[role='button'][aria-label='Submit']",
                "div[role='button']:contains('Submit')",
                "span:contains('Submit')",
                ".NPEfkd.RveJvd.snByac:contains('Submit')"
            ]
            
            submit_clicked = False
            for selector in submit_selectors:
                try:
                    submit_button = browser.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        print(f"📤 Found Submit button, clicking it...")
                        
                        # Scroll to the submit button to ensure it's visible
                        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                        time.sleep(1)
                        
                        # Click the submit button
                        submit_button.click()
                        print("✅ Form submitted successfully!")
                        submit_clicked = True
                        time.sleep(3)  # Wait for submission to process
                        break
                except Exception as e:
                    continue
            
            if not submit_clicked:
                print("❌ Could not find or click Submit button automatically")
                print("📝 Please click Submit manually to complete the form")
            
        except Exception as e:
            print(f"❌ Error during submission: {str(e)[:50]}...")
            print("📝 Please click Submit manually to complete the form")
    else:
        print("📝 Auto-submit is disabled. Please review the form and click Submit manually.")
    
    return True

def fill_form(browser, wait, person):
    # Navigate to the form first
    browser.get(form_link)
    time.sleep(3)  # Give form time to load
    
    # Use the generic form filler
    return fill_form_generic(browser, person)

def main():
    # Chrome options for better stability
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless")  # Uncomment for headless mode
    
    # Ensure test file exists for upload
    ensure_test_file_exists()
    
    # Load data from CSV file
    all_data = read_data_from_csv()
    if not all_data:
        print("❌ No data to process. Exiting...")
        return
    
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(browser, 20)
    
    try:
        print("🚀 Starting bulk form automation...")
        print(f"📊 Total entries to process: {len(all_data)}")
        print(f"⏱️ Cooldown between submissions: {COOLDOWN_SECONDS} seconds")
        
        # Step 1: Open the form URL (might redirect to login)
        print("📝 Opening form URL...")
        browser.get(form_link)
        time.sleep(3)
        
        # Check if we're on a login page
        current_url = browser.current_url
        if "accounts.google.com" in current_url:
            print("🔐 Google login required. Please log in manually...")
            print("👆 After logging in, the form should load automatically.")
            input("Press Enter after you've logged in and can see the form...")
        
        # Step 2: Process each entry from CSV
        successful_submissions = 0
        failed_submissions = 0
        
        for i, person in enumerate(all_data, 1):
            print(f"\n{'='*60}")
            print(f"📝 Processing entry {i}/{len(all_data)}")
            print(f"👤 Student: {person.get('student_email', 'N/A')}")
            print(f"📧 Partner: {person.get('partner_email', 'N/A')}")
            print(f"📅 Date: {person.get('date', 'N/A')}")
            print(f"✅ Status: {person.get('flow_status', 'N/A')}")
            print(f"{'='*60}")
            
            try:
                # Fill and submit the form
                success = fill_form(browser, wait, person)
                if success:
                    successful_submissions += 1
                    print(f"✅ Entry {i} processed successfully!")
                else:
                    failed_submissions += 1
                    print(f"❌ Entry {i} failed to process!")
                
            except Exception as e:
                failed_submissions += 1
                print(f"❌ Error processing entry {i}: {str(e)[:100]}...")
            
            # Cooldown between submissions (except for the last one)
            if i < len(all_data):
                print(f"⏳ Waiting {COOLDOWN_SECONDS} seconds before next submission...")
                for remaining in range(COOLDOWN_SECONDS, 0, -1):
                    print(f"⏱️  {remaining} seconds remaining...", end='\r')
                    time.sleep(1)
                print("✅ Cooldown complete!                    ")  # Clear the countdown line
        
        # Final summary
        print(f"\n{'='*60}")
        print("📊 FINAL SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Successful submissions: {successful_submissions}")
        print(f"❌ Failed submissions: {failed_submissions}")
        print(f"📊 Total processed: {len(all_data)}")
        print(f"📈 Success rate: {(successful_submissions/len(all_data)*100):.1f}%")
        print(f"{'='*60}")
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n✅ Script completed! Press Enter to close browser...")
        browser.quit()

if __name__ == "__main__":
    main()
