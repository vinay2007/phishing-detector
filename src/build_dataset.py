import pandas as pd
import urllib.request
import zipfile
import io
import os

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

def build_training_dataset():
    """Builds the CSV file used to train the Machine Learning models."""
    print("🚀 Starting Training Dataset Build...")

    # 1. Fetch Phishing URLs (PhishTank)
    print("📥 Downloading PhishTank data...")
    phishtank_url = "http://data.phishtank.com/data/online-valid.csv"
    try:
        with urllib.request.urlopen(phishtank_url) as response:
            phish_df = pd.read_csv(io.StringIO(response.read().decode('utf-8')))
        phish_df = phish_df[['url']]
        phish_df['label'] = 1
    except Exception as e:
        print(f"❌ PhishTank Error: {e}")
        return

    # 2. Fetch Legitimate URLs (Tranco/Umbrella)
    print("📥 Downloading Legitimate URLs for training...")
    umbrella_url = "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
    try:
        with urllib.request.urlopen(umbrella_url) as response:
            zip_content = response.read()
        zip_file = zipfile.ZipFile(io.BytesIO(zip_content))
        legit_df = pd.read_csv(zip_file.open('top-1m.csv'), header=None, names=['rank', 'domain'])

        # We take a sample to balance the dataset
        num_phish = len(phish_df)
        legit_df = legit_df.head(num_phish).copy()
        legit_df['url'] = "http://" + legit_df['domain']
        legit_df = legit_df[['url']]
        legit_df['label'] = 0
    except Exception as e:
        print(f"❌ Legitimate Data Error: {e}")
        return

    # 3. Combine and Save Training Dataset
    dataset = pd.concat([phish_df, legit_df]).sample(frac=1).reset_index(drop=True)
    dataset.to_csv('data/phishing_dataset.csv', index=False)
    print(f"✅ Training Dataset Saved: data/phishing_dataset.csv ({len(dataset)} rows)")

def build_app_whitelist():
    """Builds the TXT file used by the app to skip scanning trusted sites."""
    print("\n🚀 Starting App Whitelist Build...")

    # We use the Tranco Top 10,000 domains as our "Gold Standard" whitelist
    umbrella_url = "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
    try:
        with urllib.request.urlopen(umbrella_url) as response:
            zip_content = response.read()
        zip_file = zipfile.ZipFile(io.BytesIO(zip_content))
        df = pd.read_csv(zip_file.open('top-1m.csv'), header=None, names=['rank', 'domain'])

        # Take Top 10,000 for the whitelist
        whitelist = df.head(10000)['domain']

        # Save as a plain text file (one domain per line)
        with open('data/whitelist.txt', 'w') as f:
            for domain in whitelist:
                f.write(f"{domain}\n")

        print("✅ Whitelist Saved: data/whitelist.txt (Top 10,000 Domains)")
    except Exception as e:
        print(f"❌ Whitelist Build Error: {e}")

if __name__ == "__main__":
    build_training_dataset()
    build_app_whitelist()
    print("\n🎯 All data preparation complete. You can now run src/train.py")