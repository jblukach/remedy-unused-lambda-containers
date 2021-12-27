import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    ec2 = boto3.client('ec2')
    regions = ec2.describe_regions()
    
    ### Region Loop for Lambdas ###
    
    lambdas = []
    
    for region in regions['Regions']:
        
        functions = boto3.client('lambda', region_name = region['RegionName'])
        paginator = functions.get_paginator('list_functions')

        response_iterator = paginator.paginate()
        
        ### Lambda Loop ###
        
        for page in response_iterator:
            
            for function in page['Functions']:
                if function['PackageType'] == 'Image':
                    lambdas.append(function['CodeSha256'])

    ### Region Loop for Repositories ###
    
    for region in regions['Regions']:
        
        ecr = boto3.client('ecr', region_name = region['RegionName'])
        paginator = ecr.get_paginator('describe_repositories')

        response_iterator = paginator.paginate()
        
        ### Repository Loop ###
        
        for page in response_iterator:
            
            for repository in page['repositories']:
                
                paginator2 = ecr.get_paginator('list_images')

                response_iterator2 = paginator2.paginate(
                    repositoryName = repository['repositoryName'],
                )
                
                ### Image Loop ###
                
                for page2 in response_iterator2:
                    
                    for imageid in page2['imageIds']:
                        
                        parsed = imageid['imageDigest'].split(':')
                        
                        if parsed[1] not in lambdas:

                            ecr.batch_delete_image(
                                registryId = repository['registryId'],
                                repositoryName = repository['repositoryName'],
                                imageIds = [
                                    {
                                        'imageDigest': imageid['imageDigest'],
                                        'imageTag': imageid['imageTag']
                                    }
                                ]
                            )

    return {
        'statusCode': 200,
        'body': json.dumps('Delete Unused Lambda Containers')
    }