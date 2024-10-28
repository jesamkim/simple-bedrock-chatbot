class Config:
    # Stack name
    # Change this value if you want to create a new instance of the stack
    STACK_NAME = "cdk-chatbot-claude35"
    
    # Put your own custom value here to prevent ALB to accept requests from
    # other clients that CloudFront. You can choose any random string.
    CUSTOM_HEADER_VALUE = "My_random_value_59asv15e4s32"    
    
