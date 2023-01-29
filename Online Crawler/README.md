# Pre-requisites

These are the code when you want to crawl the content realtime and send to Kinesis Stream & Firehose in AWS. Here are the step-by-step instructions:

1. Set up your Twitter API keys and secrets. You can get these by creating a developer account at [this link](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api).
2. Set up your Reddit API Keys and secrets. Follow the instruction [here from PRAW](https://praw.readthedocs.io/en/stable/getting_started/authentication.html) (the library we'll use) for more detail
3. Replace the `bearer_token` for Twitter, `CLIENT_ID` and `CLIENT_SECRET` for Reddit.
4. Currently it's only print out the response. If you want to plug in Kinesis Stream, setup the pipeline on AWS and uncomment the code.

# For AWS Kinesis Stream Setup

This instruction only work with AWS Academy account. If you're using the Free Tier or Normal account, please create an IAM Role which enable all the resources sharing across S3, EC2, Kinesis, Lambda

## Kinesis Stream Note

First create 2 Kinesis Streams for 2 streaming sources, change it into the `Provisioned` mode to save cost and set the IAM role with **LabRole**.

With the IAM role given by the AWS Academy account, all the resources can be shared directly amongs services. Therefore, the stream name will be use directly from the S3 to subscribe and send data from the crawler on EC2 instances.

## EC2 Note

1. Create a new instance. Remember to set the security group and role with "Lab" keyword (`LabRole`, `LabSession`)
2. Run those commands to setup AWS CLI

```
sudo yum update
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

sudo amazon-linux-extras install docker
sudo service docker start
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

sudo chkconfig docker on
sudo yum install -y git
```

3. Create `requirements.txt` and add these package names:

```
pandas
boto3
tweepy
praw
```

Then run the install command

```
pip3 install -r requirements.txt
```

4. Create the crawling script in Python by `touch <file_name>.py` and edit with `vi <file_name>.py` command. Execute it with `python3 <file_name>.py`

## Lambda note

For the AWS Comprehend, please follow [this tutorial](https://aws.amazon.com/blogs/compute/using-aws-lambda-and-amazon-comprehend-for-sentiment-analysis/) for a more detail instruction. With the given lambda code, remember to set the environment variable `ESCALATION_INTENT_NAME` with a value of `Escalate`.

The transformed lambda function will invoke the Comprehend lambda to get the sentient label for the text for both sources. Then it will write that new fields to the object before transforming data JSON data into CSV and sending to S3 Bucket

Log of success lambda function can be seen in **CloudWatch**, which is really helpful to debug when developing on Cloud.

## Kinesis Firehose Note

Create 2 Kinesis Firehose delivery stream with the `Source` from the according Kinesis Stream created above, and the `Destination` is to the target S3 bucket for cleaned data.

Please remember to tick the Data Transformation option with Lambda and select the created function above.

# Scheduled Backup Crawling Source

Ideally, at the end of each they, Twitter API and Pushift (Reddit) API will be used to crawl all the posts within the day. The collected data will be processed by one `ProcessNotebook` and uploaded into a raw S3 bucket. From here, another `NLPNotebook` will use a state-of-the-art model (actually using the same AWS Comprehend) to label the sentiment of the sentence.

The reason why we have a different notebook is to flexibly produce different datasets based on our interest.
