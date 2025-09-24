import requests
import json
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

# --- Configuration ---
BOT_IP = "192.168.11.1"
PORT = 1448
POI_API_URL = f"http://{BOT_IP}:{PORT}/api/core/artifact/v1/pois"
NAVIGATION_API_URL = f"http://{BOT_IP}:{PORT}/api/core/motion/v1/actions"
TOPIC_NAME = "/navigation_goal"
API_TIMEOUT_SECONDS = 10
POI_JSON_FILE_PATH = "pois.json"

class NavigationPublisher(Node):
    def __init__(self):
        super().__init__('navigation_goal_publisher')
        self.publisher_ = self.create_publisher(Point, TOPIC_NAME, 10)

    def publish_status(self, message: str):
        self.get_logger().info(message)

def get_pois(poi_api, api_timeout, poi_json_path, publish_status_callback):
    try:
        response = requests.get(poi_api, timeout=api_timeout)
        if response.status_code == 200:
            pois = response.json()
            if isinstance(pois, list):
                total_pois = len(pois)
                poi_dict = {}
                poi_names = []
                for poi in pois:
                    if "metadata" in poi and "display_name" in poi["metadata"]:
                        name = poi["metadata"]["display_name"].strip().lower()
                        poi_names.append(name)
                        if "pose" in poi:
                            x = round(poi["pose"].get("x", 0.0), 3)
                            y = round(poi["pose"].get("y", 0.0), 3)
                            yaw = round(poi["pose"].get("yaw", 0.0), 3)
                            poi_dict[name] = {"x": x, "y": y, "yaw": yaw}

                with open(poi_json_path, 'w') as f:
                    json.dump(poi_dict, f, indent=4)

                publish_status_callback(f"Found {len(poi_names)} POIs")

                if total_pois > 0 and all("metadata" in poi and "display_name" in poi["metadata"] for poi in pois):
                    poi_messages = []
                    for poi in pois:
                        original_name = poi['metadata']['display_name']
                        name = original_name.strip().lower()
                        x = round(poi["pose"].get("x", 0.0), 3) if "pose" in poi else "N/A"
                        y = round(poi["pose"].get("y", 0.0), 3) if "pose" in poi else "N/A"
                        yaw = round(poi["pose"].get("yaw", 0.0), 3) if "pose" in poi else "N/A"
                        poi_messages.append(f"{original_name} (stored as {name}): (x={x}, y={y}, yaw={yaw})")
                    
                    poi_message = f"Total POIs: {total_pois}\nList of POIs with coordinates:\n"
                    poi_message += "\n".join(poi_messages)
                    poi_message += f"\nPOI list saved to {poi_json_path}"
                else:
                    poi_message = f"Total POIs: {total_pois}"
                
                publish_status_callback(poi_message)
                return poi_dict, True
            else:
                publish_status_callback("Error: POI response is not a list")
                return {}, False
        else:
            publish_status_callback(f"Failed to fetch POIs. Status: {response.status_code}")
            return {}, False
    except requests.exceptions.Timeout:
        publish_status_callback(f"Error fetching POIs: Request timed out after {api_timeout} seconds.")
        return {}, False
    except requests.exceptions.ConnectionError as e:
        publish_status_callback(f"Error fetching POIs: Connection error - {e}")
        return {}, False
    except json.JSONDecodeError as e:
        publish_status_callback(f"Error parsing POI response: Invalid JSON - {e}")
        return {}, False
    except Exception as e:
        publish_status_callback(f"An unexpected error occurred while fetching POIs: {e}")
        return {}, False

def go_to_location(x: float, y: float, yaw: float, navigation_url: str, publish_status_callback, ros_publisher):
    payload = {
        "action_name": "slamtec.agent.actions.MoveToAction",
        "options": {
            "target": {
                "x": x,
                "y": y,
                "z": 0
            },
            "move_options": {
                "mode": 0,
                "flags": ["with_yaw", "precise"],
                "yaw": yaw,
                "acceptable_precision": 0,
                "fail_retry_count": 2
            }
        }
    }

    try:
        response = requests.post(navigation_url, json=payload, timeout=10)
        if response.status_code == 200:
            publish_status_callback(f"Navigation command sent to: (x={x}, y={y}, yaw={yaw})")
            
            # Publish to ROS 2 topic
            msg = Point()
            msg.x = x
            msg.y = y
            msg.z = yaw  # Using z field to represent yaw
            ros_publisher.publish(msg)
            return True
        else:
            publish_status_callback(f"Failed to send navigation command. Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        publish_status_callback("Navigation command failed: Request timed out.")
    except requests.exceptions.ConnectionError as e:
        publish_status_callback(f"Navigation command failed: Connection error - {e}")
    except Exception as e:
        publish_status_callback(f"Unexpected error occurred: {e}")
    return False

def main():
    rclpy.init()
    node = NavigationPublisher()
    
    def ros_publish_status(msg): 
        node.publish_status(msg)
    
    ros_publisher = node.publisher_
    
    # Fetch POIs
    ros_publish_status("Fetching POIs from the server...")
    poi_dict, success = get_pois(
        poi_api=POI_API_URL,
        api_timeout=API_TIMEOUT_SECONDS,
        poi_json_path=POI_JSON_FILE_PATH,
        publish_status_callback=ros_publish_status
    )
    
    if not success:
        ros_publish_status("Failed to fetch POIs. Exiting.")
        rclpy.shutdown()
        return
    
    # Display available POIs
    ros_publish_status("\nAvailable locations:")
    for i, name in enumerate(poi_dict.keys(), 1):
        ros_publish_status(f"{i}. {name}")
    
    # Get user input
    while True:
        try:
            user_input = input("\nEnter the location name or number you want to navigate to (or 'quit' to exit): ").strip().lower()
            
            if user_input == 'quit':
                break
                
            # Check if input is a number
            if user_input.isdigit():
                index = int(user_input) - 1
                if 0 <= index < len(poi_dict):
                    location_name = list(poi_dict.keys())[index]
                else:
                    ros_publish_status("Invalid number. Please try again.")
                    continue
            else:
                location_name = user_input
            
            # Check if location exists
            if location_name in poi_dict:
                location = poi_dict[location_name]
                ros_publish_status(f"Navigating to {location_name} at coordinates (x={location['x']}, y={location['y']}, yaw={location['yaw']})")
                
                # Send navigation command
                success = go_to_location(
                    x=location['x'],
                    y=location['y'],
                    yaw=location['yaw'],
                    navigation_url=NAVIGATION_API_URL,
                    publish_status_callback=ros_publish_status,
                    ros_publisher=ros_publisher
                )
                
                if success:
                    ros_publish_status("Navigation command sent successfully!")
                else:
                    ros_publish_status("Failed to send navigation command.")
                
                # Ask if user wants to navigate to another location
                another = input("Navigate to another location? (y/n): ").strip().lower()
                if another != 'y':
                    break
            else:
                ros_publish_status(f"Location '{location_name}' not found. Please try again.")
                
        except KeyboardInterrupt:
            ros_publish_status("\nExiting...")
            break
        except Exception as e:
            ros_publish_status(f"An error occurred: {e}")
    
    rclpy.shutdown()

if __name__ == "__main__":
    main()
