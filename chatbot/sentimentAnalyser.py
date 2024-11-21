from textblob import TextBlob

class SentimentAnalyzer:
    @staticmethod
    def analyze_sentiment(text):
        """
        Analyze the sentiment of the given text.
        Returns a tuple of (sentiment_label, sentiment_score).
        """
        analysis = TextBlob(text)
        
        # Get the polarity score (-1 to 1)
        polarity = analysis.sentiment.polarity
        
        # Classify the sentiment
        if polarity > 0.05:
            return ("positive", polarity)
        elif polarity < -0.05:
            return ("negative", polarity)
        else:
            return ("neutral", polarity)

    @staticmethod
    def get_sentiment_stats(sentiments):
        """
        Calculate sentiment statistics from a list of sentiment labels.
        Returns a dictionary with counts and percentages.
        """
        total = len(sentiments)
        counts = {
            "positive": sentiments.count("positive"),
            "neutral": sentiments.count("neutral"),
            "negative": sentiments.count("negative")
        }
        
        percentages = {
            key: (value / total) * 100 for key, value in counts.items()
        }
        
        return {
            "counts": counts,
            "percentages": percentages
        }