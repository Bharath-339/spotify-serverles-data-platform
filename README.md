# Spotify Serverless Data Platform

A fully automated, serverless data pipeline that fetches Spotify playlist data, transforms it, and makes it queryable via AWS Athena. Built with AWS Lambda, S3, Glue, and Athena.

## 🏗️ Architecture

```
CloudWatch Events (Daily Trigger)
    ↓
Load Lambda (fetch-spotify-data)
    ↓
S3 Raw Data (/raw/)
    ↓
S3 Event Notification
    ↓
Transform Lambda (transform-data)
    ↓
S3 Processed Data (/processed/)
    ↓
AWS Glue Crawler (schema detection)
    ↓
Glue Data Catalog
    ↓
Amazon Athena (SQL queries)
```

### Data Flow
1. **CloudWatch Events**: Triggers the Load Lambda function daily
2. **Load Lambda**: Fetches Spotify playlist track data and writes raw JSON to S3
3. **S3 Event Notification**: Automatically invokes Transform Lambda when new data arrives
4. **Transform Lambda**: Flattens and normalizes the data (albums, artists, songs), removes duplicates, and writes CSV files to S3
5. **Glue Crawler**: Automatically crawls the processed data and creates/updates table schemas
6. **Athena**: Provides SQL query interface to analyze the data

## 📊 Data Models

### Albums Table
- `id` (string): Unique album identifier
- `name` (string): Album name
- `release_date` (date): Album release date
- `total_tracks` (integer): Number of tracks in album
- `url` (string): Spotify URL

### Artists Table
- `artist_id` (string): Unique artist identifier
- `artist_name` (string): Artist name
- `external_url` (string): Spotify profile URL

### Songs Table
- `song_id` (string): Unique song identifier
- `song_name` (string): Song name
- `duration_ms` (integer): Duration in milliseconds
- `url` (string): Spotify URL
- `popularity` (integer): Popularity score (0-100)
- `song_added` (timestamp): When song was added to playlist
- `album_id` (string): Foreign key to albums table
- `artist_id` (string): Foreign key to artists table

## 🚀 Prerequisites

- AWS Account
- S3 bucket created
- IAM role created with necessary permissions
- Spotify API credentials (Client ID and Secret)

## 📋 Setup & Deployment

### 1. Clone the Repository
```bash
git clone <repository-url>
cd spotify-serverless-data-platform
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

### 3. Set Up Spotify API Credentials
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an application to get your Client ID and Client Secret
3. Store these credentials securely - you'll need them during deployment

### 4. Update CloudFormation Parameters
Edit `cloudformation/pipeline.json` and update the following default parameters:
- `BucketName`: Your existing S3 bucket name
- `ExecutionRoleArn`: Your existing IAM role ARN
- `SpotifyClientId`: Your Spotify API Client ID
- `SpotifyClientSecret`: Your Spotify API Client Secret

### 5. Package Lambda Functions

**Load Lambda:**
```bash
cd load-lambda
pip install -r requirements.txt -t src/
zip -r load-lambda.zip src/
aws s3 cp load-lambda.zip s3://<bucket-name>/spotify-serverless-data/files/
cd ..
```

**Transform Lambda:**
```bash
cd transform-lambda
pip install -r requirements.txt -t src/
zip -r transform-lambda.zip src/
aws s3 cp transform-lambda.zip s3://<bucket-name>/spotify-serverless-data/files/
cd ..
```

### 6. Deploy CloudFormation Stack
```bash
aws cloudformation create-stack \
  --stack-name spotify-serverless-pipeline \
  --template-body file://cloudformation/pipeline.json \
  --parameters \
    ParameterKey=BucketName,ParameterValue=<your-bucket-name> \
    ParameterKey=ExecutionRoleArn,ParameterValue=arn:aws:iam::<account-id>:role/ap-southeast-2-data-pipeline-role \
    ParameterKey=SpotifyClientId,ParameterValue=<spotify-client-id> \
    ParameterKey=SpotifyClientSecret,ParameterValue=<spotify-client-secret> \
  --capabilities CAPABILITY_NAMED_IAM
```

## 🔐 Required IAM Permissions

Your IAM role needs the following permissions:

### S3 Permissions
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::your-bucket-name",
    "arn:aws:s3:::your-bucket-name/*"
  ]
}
```

### Lambda & CloudWatch Permissions
```json
{
  "Effect": "Allow",
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "arn:aws:logs:*:*:*"
}
```

### Glue & Athena Permissions
```json
{
  "Effect": "Allow",
  "Action": [
    "glue:*",
    "athena:*"
  ],
  "Resource": "*"
}
```

See `policies/` folder for complete policy documents.

## 💾 S3 Bucket Structure

Your S3 bucket should have the following structure:

```
your-bucket-name/
├── spotify-serverless-data/
│   ├── files/              # Lambda deployment packages
│   │   ├── load-lambda.zip
│   │   └── transform-lambda.zip
│   └── platform/
│       ├── raw/            # Raw data from Load Lambda
│       │   └── data.json
│       ├── processed/      # Transformed data from Transform Lambda
│       │   ├── albums.csv
│       │   ├── artists.csv
│       │   └── songs.csv
│       └── athena-results/ # Athena query results
```

## 🔧 Configuration

### Environment Variables (Lambda)

**Load Lambda:**
- `BUCKET_NAME`: S3 bucket name
- `BUCKET_PATH`: Path within bucket (e.g., `spotify-serverless-data/platform/raw/data.json`)
- `SPOTIFY_CLIENT_ID`: Spotify API Client ID
- `SPOTIFY_CLIENT_SECRET`: Spotify API Client Secret

**Transform Lambda:**
- `BUCKET_NAME`: S3 bucket name
- `BUCKET_PATH`: Path within bucket (e.g., `spotify-serverless-data/platform/raw/data.json`)

### CloudWatch Trigger
- **Schedule**: Daily (default: `rate(1 day)`)
- **Customization**: Edit the `ScheduleRule` in `cloudformation/pipeline.json` to change frequency

## 📊 Querying with Athena

Once the pipeline runs, you can query the data using Athena:

### Example Queries

**Most Popular Songs:**
```sql
SELECT song_name, artist_name, popularity
FROM spotify_data.songs s
JOIN spotify_data.artists a ON s.artist_id = a.artist_id
ORDER BY popularity DESC
LIMIT 10;
```

**Albums by Release Date:**
```sql
SELECT name, release_date, total_tracks
FROM spotify_data.albums
ORDER BY release_date DESC;
```

**Artist Activity:**
```sql
SELECT artist_name, COUNT(*) as song_count
FROM spotify_data.songs s
JOIN spotify_data.artists a ON s.artist_id = a.artist_id
GROUP BY artist_name
ORDER BY song_count DESC;
```

## 📝 Environment Setup

Create a `.env` file in the project root for local development:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
BUCKET_NAME=your-bucket-name
BUCKET_PATH=spotify-serverless-data/platform/raw/data.json
```

## 🧪 Local Testing

### Test Load Lambda
```python
from load-lambda.src.main import handler

event = {}
context = {}
handler(event, context)
```

### Test Transform Lambda
```python
from transform-lambda.src.main import handler

event = {}
context = {}
handler(event, context)
```

## 📈 Monitoring

### CloudWatch Logs
- **Load Lambda**: `/aws/lambda/spotify-load-lambda`
- **Transform Lambda**: `/aws/lambda/spotify-transform-lambda`

### Key Metrics to Monitor
- Lambda execution time and errors
- S3 object count and size
- Glue Crawler success/failure
- Athena query execution time

## 🔄 Troubleshooting

### Common Issues

**Lambda Timeout**
- Increase timeout in CloudFormation template
- Default is 900 seconds (15 minutes)

**S3 Access Denied**
- Verify IAM role has S3 permissions
- Check bucket policy allows the role

**Spotify API Error**
- Verify credentials are correct
- Check Spotify API rate limits
- Ensure playlist URL is valid and public

**Glue Crawler Not Finding Data**
- Verify processed data folder path matches Crawler target
- Check data format (CSV/JSON)
- Ensure IAM role has S3 read permissions

## 🛠️ Development

### Project Structure
```
spotify-serverless-data-platform/
├── README.md                          # This file
├── requirements.txt                   # Production dependencies
├── requirements.dev.txt              # Development dependencies
├── load-lambda/
│   ├── src/
│   │   ├── main.py                   # Lambda handler
│   │   └── spotify.py                # Spotify API client
│   ├── load-lambda.zip               # Deployment package
│   └── requirements.txt
├── transform-lambda/
│   ├── src/
│   │   ├── main.py                   # Lambda handler
│   │   ├── helper.py                 # Data transformation utilities
│   │   └── requirements.txt
│   └── transform-lambda.zip          # Deployment package
└── cloudformation/
    └── pipeline.json                 # CloudFormation template
```

### Dependencies

**Production:**
- `requests`: HTTP library for API calls
- `boto3`: AWS SDK for Python
- `spotipy`: Spotify Web API Python library
- `pandas`: Data manipulation library

**Development:**
- `python-dotenv`: Environment variable management

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👤 Author

Bharath Matta

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

**Last Updated**: July 2026

