# Use the AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.10

# Set the function directory
ARG FUNCTION_DIR="/var/task/"

# Set the working directory
WORKDIR ${FUNCTION_DIR}

# Copy the application code into the Docker image
COPY . ${FUNCTION_DIR}

# Install dependencies (including Zappa)
RUN pip install -r requirements.txt

# Grab the Zappa handler and copy it into the working directory
RUN pip install zappa && \
    ZAPPA_HANDLER_PATH=$(python -c "from zappa import handler; print(handler.__file__)") && \
    cp $ZAPPA_HANDLER_PATH ${FUNCTION_DIR}/handler.py

# Specify the Lambda function handler to invoke
CMD ["handler.lambda_handler"]
