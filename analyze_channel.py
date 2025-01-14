import os
from dotenv import load_dotenv
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

# Load environment variables from .env file
load_dotenv()

# Get CHANNEL_ID from .env
CHANNEL_ID = os.getenv('CHANNEL_ID')

folder_path = f"data/{CHANNEL_ID}"

files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
last_file = max(files, key=os.path.getmtime) if files else None
print(last_file)

# Load the data
df = pd.read_csv(last_file)

df['Engagement Rate (%)'] = ((df['Like Count'] + df['Comments Count']) / df['View Count']) * 100

category_analysis = df.groupby('Category').agg({
    'View Count': 'mean',
    'Like Count': 'mean',
    'Comments Count': 'mean',
    'Engagement Rate (%)': 'mean'
}).sort_values(by='View Count', ascending=False)
print(category_analysis)

text = " ".join(title for title in df['Title'])
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

low_engagement = df[df['Engagement Rate (%)'] < df['Engagement Rate (%)'].mean()]
print(low_engagement[['Title', 'Category', 'Engagement Rate (%)']])

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

sns.barplot(x=category_analysis.index, y='View Count', data=category_analysis)
plt.xticks(rotation=45, ha='right')
plt.title('Average Views by Category')
plt.show()