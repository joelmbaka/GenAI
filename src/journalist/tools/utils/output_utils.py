from dateutil.parser import parse
import json
from datetime import datetime
from journalist.tools.utils.models import TweetCollectionModel

def format_tweet_collection(tweets_collected, trend):
    """
    Format collected tweets into a TweetCollectionModel
    
    Args:
        tweets_collected: List of collected tweet models
        trend: The trend that was searched for
        
    Returns:
        TweetCollectionModel: A structured collection of tweets
    """
    return TweetCollectionModel(
        status="success",
        trend=trend,
        tweet_count=len(tweets_collected),
        tweets=tweets_collected,
        filename=f"tweets_{trend.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

def prepare_tweets_json(tweet_collection):
    """
    Convert a TweetCollectionModel to a JSON-serializable dictionary
    
    Args:
        tweet_collection: TweetCollectionModel with tweet data
        
    Returns:
        dict: A dictionary suitable for JSON serialization
    """
    return {
        "tweets": [
            {
                "id": tweet.structure.id,
                "content": tweet.content,
                "user": tweet.user.handle,
                "timestamp": parse(tweet.timestamp.datetime).isoformat() if tweet.timestamp.datetime else None,
                "likes": int(tweet.metrics.likes) if tweet.metrics.likes else 0,
                "retweets": int(tweet.metrics.retweets) if tweet.metrics.retweets else 0,
                "url": f"https://twitter.com/{tweet.user.handle.lstrip('@')}/status/{tweet.structure.id}" if tweet.user.handle else f"https://twitter.com/status/{tweet.structure.id}",
                "has_photos": tweet.media.hasPhotos,
                "has_videos": tweet.media.hasVideos,
                "photo_urls": tweet.media.photoUrls,
            }
            for tweet in tweet_collection.tweets
        ]
    }

def format_success_response(tweets_data):
    """
    Format a successful response as a JSON string
    
    Args:
        tweets_data: Dictionary containing tweet data
        
    Returns:
        str: JSON string with success status and tweet data
    """
    return json.dumps({
        'status': 'success',
        'tweet_count': len(tweets_data['tweets']),
        'tweets': tweets_data['tweets']
    })

def format_error_response(error_message="", filename=""):
    """
    Format an error response as a JSON string
    
    Args:
        error_message: Optional error message
        filename: Optional filename where error details were saved
        
    Returns:
        str: JSON string with error status
    """
    response = {
        'status': 'error',
        'tweets': []
    }
    
    if error_message:
        response['error'] = error_message
    
    if filename:
        response['filename'] = filename
    
    return json.dumps(response)

def format_cookies_error(error):
    """
    Format an error response for cookie loading failure
    
    Args:
        error: The exception that occurred
        
    Returns:
        str: JSON string with error details
    """
    filename = f"error_cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return format_error_response(
        error_message=f"Error loading cookies: {str(error)}", 
        filename=filename
    )

def format_empty_response():
    """
    Format a response for when no tweets were found
    
    Returns:
        str: JSON string with empty tweets list
    """
    return json.dumps({
        'tweets': []
    }) 