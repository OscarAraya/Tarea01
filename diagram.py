# Created by Araya O. 08/08/2025
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import CloudFront, Route53, ElbApplicationLoadBalancer, APIGateway
from diagrams.aws.database import RDSPostgresqlInstance
from diagrams.aws.blockchain import Blockchain
from diagrams.aws.compute import LambdaFunction, ElasticKubernetesService
from diagrams.aws.engagement import SimpleEmailServiceSes
from diagrams.aws.security import WAF
from diagrams.aws.management import Cloudwatch
from diagrams.aws.storage import SimpleStorageServiceS3
from diagrams.generic.storage import Storage
from diagrams.k8s.compute import Pod
from diagrams.k8s.storage import Volume
from diagrams.k8s.network import Ingress

with Diagram("OpenDID Suggested Architecture", show=True):
    
    with Cluster("Legacy Systems"):
            legacy_storage = Storage("Legacy Storage")

    with Cluster("VPC"):

        with Cluster("DNS Zone"):
            zone_rt53 = Route53("DNS Zone")

        email_service = SimpleEmailServiceSes("Mail Service (SES)")

        k8s_service = ElasticKubernetesService("AWS EKS")

        with Cluster("Presentation Layer"):
            cloud_front = CloudFront("AWS CloudFront")
            api_gateway = APIGateway("AWS API Gateway")
            firewall = WAF("AWS WAF")

            cloud_front - firewall - api_gateway
    
        with Cluster("Application Layer"):
            with Cluster("verifier-services-ns"):
                verifier_pod = Pod("Verifier Service")

            with Cluster("issuer-services-ns"):
                issuer_pod = Pod("Issuer Service")

                app_issuer = issuer_pod

            with Cluster("capp-services-ns"):
                 capp_pod = Pod("CApp Service")
                 load_balancer = ElbApplicationLoadBalancer("App Load Balancer")
                 lambda_function = LambdaFunction("Lambda Function")
                 cloud_watch = Cloudwatch("AWS CloudWatch")
                 ingress = Ingress("Ingress")

                 load_balancer - capp_pod - lambda_function - cloud_watch

            with Cluster("wallet-services-ns"):
                wallet_pod = Pod("Wallet Service")
                certificate_volume = Volume("Certificate Volume")
                
                wallet_pod - certificate_volume

            with Cluster("external-services-ns"):
                notification_pod = Pod("Notification Service")

            with Cluster("user-services-ns"):
                 user_service_pod = Pod("User Service")
                 user_s3 = SimpleStorageServiceS3("S3 Bucket")

                 user_service_pod - user_s3

                 user_namespace = [user_service_pod, user_s3]

            with Cluster("trusted-services-ns"):
                trust_agent_pod = Pod("Trust Agent")

            with Cluster("Database Layer"):
                postgres_pod = RDSPostgresqlInstance("PostgreSQL")
                blockchain_pod = Blockchain("HyperLedger Fabric")

                # Database and Fabric interaction
                postgres_pod - blockchain_pod

                # Send Message to User
                trust_agent_pod >> Edge(color='blue') >> notification_pod
                # Issue VC (opt ZKP)
                trust_agent_pod >> Edge(color='darkred') >> issuer_pod
                # Read/Write
                trust_agent_pod >> Edge(color='red') >> postgres_pod

                # Send offer message to User
                issuer_pod >> Edge(color='blue') >> notification_pod
                # Read/Write
                issuer_pod >> Edge(color='red') >> postgres_pod

                # Send message to User
                verifier_pod >> Edge(color='blue') >> notification_pod
                # Read/Write
                verifier_pod >> Edge(color='red') >> postgres_pod

                # Ingress
                ingress >> Edge(color='darkgreen') >> capp_pod
                # Present VP or ZKP
                capp_pod >> Edge(color='black') >> verifier_pod
                # Wallet Attestation / Sign Wallet Keys
                capp_pod >> Edge(color='darkorange') >> wallet_pod
                # Read Blockchain
                capp_pod >> Edge(color='gray') >> user_service_pod
                # Read Volume
                capp_pod >> Edge(color='darkorange') >> certificate_volume
                # Register Wallet and User Issue VC | Report Lost and Found | Cancel Membership
                capp_pod >> Edge(color='darkblue') >> trust_agent_pod

                # Read
                wallet_pod >> Edge(color='red') >> postgres_pod

                # Read
                user_service_pod >> Edge(color='red') >> postgres_pod

                # API Gateway Connection
                cloud_front >> Edge(color='darkgreen') >> capp_pod

                # Offer Data to Issue
                legacy_storage >> Edge(color='darkred') >> issuer_pod

                # Take verified VC or ZKP from Holder
                verifier_pod >> Edge(color='brown') >> legacy_storage

                # DNS Lookup
                zone_rt53 >> Edge(color='purple') >> cloud_front

                # Send notification through Mail Service
                notification_pod >> Edge(color='blue') >> email_service