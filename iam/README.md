\# IAM Security Design



This project uses AWS IAM roles and policies to control access between services using the principle of least privilege where possible.



\## Lambda Execution Role



The Spotify extraction Lambda requires:



\- CloudWatch Logs permissions

\- `s3:PutObject` permission for the Raw S3 prefix



Target:



```text

raw/spotify/\*

