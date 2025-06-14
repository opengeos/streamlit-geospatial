from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.types import Prediction
from google.cloud.exceptions import GoogleCloudError
import config

def get_vertex_endpoint(project_id: str = config.VERTEX_AI_PROJECT_ID,
                        location: str = config.VERTEX_AI_LOCATION,
                        endpoint_id: str = config.VERTEX_AI_ENDPOINT_ID) -> aiplatform.Endpoint | None:
    """
    Initializes connection to Vertex AI and gets a specific endpoint.

    Args:
        project_id (str, optional): Your Google Cloud project ID. Defaults to config.VERTEX_AI_PROJECT_ID.
        location (str, optional): The region where your endpoint is located. Defaults to config.VERTEX_AI_LOCATION.
        endpoint_id (str, optional): The ID of the Vertex AI endpoint. Defaults to config.VERTEX_AI_ENDPOINT_ID.

    Returns:
        aiplatform.Endpoint | None: The endpoint object if successful, None otherwise.
    """
    try:
        aiplatform.init(project=project_id, location=location)
        endpoint = aiplatform.Endpoint(endpoint_name=endpoint_id)
        # Attempt a simple operation to check if endpoint is valid, like getting its display name
        _ = endpoint.display_name
        return endpoint
    except GoogleCloudError as e:
        print(f"Error initializing Vertex AI or getting endpoint: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred with Vertex AI endpoint '{endpoint_id}': {e}")
        return None

def get_prediction(endpoint: aiplatform.Endpoint, instance_data: dict) -> dict | None:
    """
    Gets a prediction from a Vertex AI endpoint.

    Args:
        endpoint (aiplatform.Endpoint): The Vertex AI endpoint object.
        instance_data (dict): The instance data for which to get a prediction.
                            Structure depends on the model's expected input.

    Returns:
        dict | None: The prediction result as a dictionary if successful, None otherwise.
    """
    try:
        prediction_result: Prediction = endpoint.predict(instances=[instance_data])
        if prediction_result.predictions:
            # Assuming the prediction output is a dict-like structure
            # The actual structure of predictions[0] can vary based on the model
            return dict(prediction_result.predictions[0])
        else:
            print("Prediction request successful, but no predictions returned.")
            return None
    except GoogleCloudError as e:
        print(f"Error during Vertex AI prediction: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during Vertex AI prediction: {e}")
        return None
