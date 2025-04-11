from my_journalistic_crew.models.TwitterElements import TweetModel, UserModel, TimestampModel, MetricsModel, MediaModel, TweetStructureModel
from selenium.webdriver.common.by import By
import datetime

def extract_tweet_data(tweet_element, tweet_id=None, driver=None) -> TweetModel:
    # Extract user info
    user_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
    user = UserModel(
        name=user_element.find_element(By.CSS_SELECTOR, 'span').text,
        handle=f'@{user_element.find_element(By.CSS_SELECTOR, 'a[role="link"]').get_attribute('href').split('/')[-1]}'
    )

    # Extract content
    content = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]').text

    # Extract timestamp
    time_element = tweet_element.find_element(By.CSS_SELECTOR, 'time')
    timestamp = TimestampModel(
        display=time_element.text,
        datetime=time_element.get_attribute('datetime')
    )

    # Extract metrics
    metrics = MetricsModel(
        replies=int(tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="reply"]').text or 0) if tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="reply"]').text.isdigit() else 0,
        retweets=int(tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]').text or 0) if tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]').text.isdigit() else 0,
        likes=int(tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="like"]').text or 0) if tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="like"]').text.isdigit() else 0
    )

    # Extract media
    photo_elements = tweet_element.find_elements(By.CSS_SELECTOR, 'img[src*="media"]')
    media = MediaModel(
        hasPhotos=bool(photo_elements),
        mediaCount=len(photo_elements),
        photoUrls=[img.get_attribute('src') for img in photo_elements]
    )

    # Create structure
    structure = TweetStructureModel(
        id=tweet_id or tweet_element.get_attribute("data-tweet-id"),
        tagName=tweet_element.tag_name,
        dataTestId=tweet_element.get_attribute('data-testid'),
        text=content
    )

    return TweetModel(
        user=user,
        content=content,
        timestamp=timestamp,
        metrics=metrics,
        media=media,
        structure=structure
    ) 