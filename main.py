import requests
import re
import random
import time
import json

# Function to get headers with random user agent
def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36',
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

# Function to check if cookies are valid and extract user details
def validate_cookies(cookies):
    try:
        cookies_dict = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookies.split('; ')}
        session = requests.Session()
        response = session.get('https://www.facebook.com/', cookies=cookies_dict, headers=get_headers())

        if response.status_code == 200 and 'c_user' in cookies_dict:
            # Extract account name from the response (if possible)
            account_name = re.search(r'<title>(.*?)</title>', response.text)
            if account_name:
                print(f"Account Name: {account_name.group(1)}")
            return cookies_dict, account_name.group(1) if account_name else "Unknown"
        else:
            print("Invalid cookies. Please check and try again.")
            return None, None
    except Exception as e:
        print(f"Error validating cookies: {e}")
        return None, None

# Function to post a comment on the given post ID
def comment_on_post(post_id, comment_text, cookies_dict):
    try:
        # Check if post_id is numeric
        if not post_id.isdigit():
            print("Invalid post ID. Please enter a numeric post ID.")
            return

        # Extract the post URL
        post_url = f"https://www.facebook.com/{post_id}"
        session = requests.Session()
        response = session.get(post_url, cookies=cookies_dict, headers=get_headers())

        if response.status_code != 200:
            print(f"Failed to load the post. Status Code: {response.status_code}")
            return

        # Extract necessary tokens from the response
        try:
            fb_dtsg = re.search(r'"fb_dtsg":"(.*?)"', response.text).group(1)
            jazoest = re.search(r'name="jazoest" value="(.*?)"', response.text).group(1)
            comment_id = re.search(r'name="comment_logging_context"\s*value="(.*?)"', response.text).group(1)
        except AttributeError as e:
            print("Failed to extract necessary tokens. Check the cookies and try again.")
            return

        # Extract action form URL
        action_url = re.search(r'"comment_box_submit_uri":"(.*?)"', response.text)
        if action_url:
            form_action = action_url.group(1).replace("\\/", "/")
        else:
            print("Failed to extract form action URL.")
            return

        # Prepare payload for commenting
        payload = {
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'comment_text': comment_text,
            'comment_logging_context': comment_id,
            'submit': 'Post'
        }

        # Send the POST request to post comment
        comment_response = session.post(form_action, data=payload, cookies=cookies_dict, headers=get_headers())

        # Check if the comment was posted
        if "success" in comment_response.url or "comment_id" in comment_response.text:
            print(f"Comment posted successfully: {comment_text}")
        else:
            print("Failed to post comment. You may be blocked from commenting.")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Main script execution
def main():
    cookies = input("Enter your Facebook cookies: ")
    post_id = input("Enter the Facebook Post ID: ")
    comment_text = input("Enter your comment: ")
    min_delay = int(input("Enter minimum delay time (seconds): "))
    max_delay = int(input("Enter maximum delay time (seconds): "))

    # Validate cookies
    cookies_dict, account_name = validate_cookies(cookies)
    if not cookies_dict:
        return  # Exit if cookies are invalid

    # If cookies are valid, proceed with further process
    print(f"Account Name: {account_name}")
    print(f"Post ID: {post_id}")
    
    # Commenting process with delay
    while True:
        try:
            comment_on_post(post_id, comment_text, cookies_dict)
            delay = random.randint(min_delay, max_delay)
            print(f"Waiting for {delay} seconds before next comment...")
            time.sleep(delay)
        except KeyboardInterrupt:
            print("\nScript stopped by the user.")
            break
        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
