# import requests

# def fetch_student_profile(student_id: str):
#     url = f"https://lms.prismaticcrm.com/api/student-profile/{student_id}"
#     try:
#         response = requests.get(url)
#         print(f"[DEBUG] Status Code: {response.status_code}")
#         print(f"[DEBUG] Raw Response: {response.text}")

#         # Try to parse JSON only if there is a body
#         if response.text.strip() == "":
#             return {
#                 "error": f"Empty response body (HTTP {response.status_code})"
#             }

#         data = response.json()

#         if response.status_code == 200:
#             return data
#         else:
#             return {
#                 "error": f"Failed to fetch student data: {response.status_code}",
#                 "response_body": data
#             }

#     except requests.RequestException as e:
#         print(f"[ERROR] Request failed: {e}")
#         return {"error": f"Request error: {e}"}
#     except Exception as e:
#         print(f"[ERROR] General error: {e}")
#         return {"error": f"Unexpected error: {e}"}


import requests
import json

def fetch_student_profile(student_id: str):
    url = f"https://lms.prismaticcrm.com/api/student-profile/{student_id}"
    try:
        response = requests.get(url)
        print(f"[DEBUG] Status Code: {response.status_code}")
        print(f"[DEBUG] Content-Type: {response.headers.get('Content-Type')}")

        if "application/json" not in response.headers.get("Content-Type", ""):
            return {
                "error": "Invalid response format: expected JSON",
                "raw_body": response.text
            }

        if response.text.strip() == "":
            return {"error": f"Empty response body (HTTP {response.status_code})"}

        data = response.json()
        print("[DEBUG] Full JSON response:")
        print(json.dumps(data, indent=2))  # Pretty print for dev logs

        if response.status_code == 200:
            return data
        else:
            return {
                "error": f"Failed to fetch student data: {response.status_code}",
                "response_body": data
            }

    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return {"error": f"Request error: {e}"}
    except Exception as e:
        print(f"[ERROR] General error: {e}")
        return {"error": f"Unexpected error: {e}"}
