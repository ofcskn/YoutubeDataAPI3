from collections import Counter
import os
from dotenv import load_dotenv
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import seaborn as sns

# Function to analyze video's category, keywords, description, and title
def analyze_video_content(data_path):
    """
    Analyze video's category, keywords, description, and title based on provided CSV data.

    Args:
        data_path (str): Path to the CSV file containing video data.

    Returns:
        dict: A dictionary containing analysis results for categories, keywords, descriptions, and titles.
    """
    try:
        # Load the CSV file
        df = pd.read_csv(data_path)

        # Initialize analysis results
        analysis_results = {
            "category_keywords": {},
            "description_keywords": {},
            "title_keywords": {},
        }

        # Get Engagement Rate by comment, like and view count
        df['Engagement Rate (%)'] = ((df['Like Count'] + df['Comments Count']) / df['View Count']) * 100

        category_analysis = df.groupby('Category').agg({
            'View Count': 'mean',
            'Like Count': 'mean',
            'Comments Count': 'mean',
            'Engagement Rate (%)': 'mean'
        }).sort_values(by='View Count', ascending=False)

        analysis_results["category_analysis"] = category_analysis

        # Analyze categories and associated keywords
        if "Category" in df.columns and "Tags (Keywords)" in df.columns:
            category_keywords = (
                df.groupby("Category")["Tags (Keywords)"]
                .apply(lambda x: ",".join(x.dropna()))
                .to_dict()
            )
            analysis_results["category_keywords"] = {
                category: Counter(re.split(r",| ", keywords.lower()))
                for category, keywords in category_keywords.items()
            }

        # Analyze description keywords
        if "Description Keywords" in df.columns:
            all_description_keywords = ",".join(df["Description Keywords"].dropna())
            analysis_results["description_keywords"] = Counter(
                re.split(r",| ", all_description_keywords.lower())
            )

        # Analyze title keywords
        if "Title" in df.columns:
            all_titles = " ".join(df["Title"].dropna())
            analysis_results["title_keywords"] = Counter(
                re.findall(r"\b\w+\b", all_titles.lower())
            )

        return analysis_results

    except FileNotFoundError:
        print("Error: The specified CSV file was not found.")
    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
    except KeyError as e:
        print(f"Error: Missing expected column in the data - {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

# Function to visualize caategory by engagement
def visualize_category(category_analysis, title):
    sns.barplot(x=category_analysis.index, y="View Count", data=category_analysis)
    plt.xticks(rotation=45, ha='right')
    plt.title(title)
    plt.show()

# Function to visualize keywords using a word cloud
def visualize_keywords(keyword_data, title):
    """
    Visualize keywords using a word cloud.

    Args:
        keyword_data (Counter): A Counter object containing keyword frequencies.
        title (str): Title for the word cloud visualization.
    """
    try:
        wordcloud = WordCloud(
            width=800, height=400, background_color="white"
        ).generate_from_frequencies(keyword_data)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.title(title, fontsize=16)
        plt.axis("off")
        plt.show()

    except ValueError:
        print("Error: No valid data available for word cloud visualization.")
    except Exception as e:
        print(f"An unexpected error occurred during visualization: {str(e)}")

if __name__ == "__main__":

    # Load environment variables from .env file
    load_dotenv()

    # Get CHANNEL_ID from .env
    CHANNEL_ID = os.getenv('CHANNEL_ID')

    folder_path = f"data/{CHANNEL_ID}"

    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    last_file_path = max(files, key=os.path.getmtime) if files else None
    
    # Analyze video content
    analysis = analyze_video_content(last_file_path)

    if analysis:
        # Visualize category keywords
        for category, keywords in analysis["category_keywords"].items():
            visualize_keywords(keywords, f"Keywords for Category: {category}")

        # Visualize description keywords
        visualize_keywords(
            analysis["description_keywords"], "Keywords from Descriptions"
        )

        # Visualize category engagements
        visualize_category(analysis["category_analysis"], "Categories by Engagement Rate")

        # Visualize title keywords
        visualize_keywords(
            analysis["title_keywords"], "Keywords from Titles"
        )