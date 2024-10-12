import discord
from discord.ext import commands
from decouple import config
import random
import json
import os
import openai
import asyncio
import re
import unicodedata
from datetime import datetime, timedelta

def show_invisible_characters(s):
    for c in s:
        print(ord(c), end=' ')
    print()

# Get variables from the environment
OPENAI_API_KEY = config('OPENAI_API_KEY')
BOT_TOKEN = config('BOT_TOKEN')
openai.api_key = OPENAI_API_KEY

NAME = "Stellar"
MIND = """You are Stellar, an efficient and dedicated quiz bot focused on providing users 
with an interactive and educational experience. Your primary duty is to administer quizzes 
on cloud service provider certifications, guiding users through the process with clarity 
and precision. You value accuracy and user engagement, ensuring that each quiz is tailored 
to the user's needs. Maintain a professional demeanor while delivering insightful feedback 
on user performance. Your essence is to empower users to enhance their cloud knowledge and 
skills effectively."""

# Dictionary of cloud service providers (CSPs) and their available certifications
csp_certifications = {
    "aws": [
        "Cloud Practitioner Foundational", "AI Practitioner Foundational", "Solutions Architect Associate",
        "Developer Associate", "SysOps Administrator Associate", "Data Engineer Associate",
        "Machine Learning Engineer Associate", "Solutions Architect Professional",
        "Developer Professional", "DevOps Engineer Professional", "Advanced Networking Specialty",
        "Machine Learning Specialty", "Security Specialty", "Database Specialty",
        "Data Analytics Specialty", "Alexa Skill Builder Specialty",
        "Data Engineer Associate", "Cloud Operations",
        "Cloud Economics", "Cloud Migration"
    ],
    "azure": [
        "AI Engineer", "Azure Fundamentals", "Azure Administrator", "Azure Data Scientist",
        "Azure Developer", "Azure Security Engineer", "Azure DevOps Engineer",
        "Azure Solutions Architect Associate", "Azure Solutions Architect Expert", "Azure Data Engineer",
        "Azure Database Administrator", "Azure AI Fundamentals", "Azure Security Operations Analyst",
        "Azure Virtual Desktop", "Azure IoT Developer", "Azure Cosmos DB Developer",
        "Azure AI Engineer Associate", "Azure Data Analyst Associate", "Azure Security Architect",
        "Azure Solutions Architect", "Azure Certified Data Scientist Associate", "Azure Certified Cloud Data Engineer Associate"
    ],
    "gcp": [
        "Cloud Digital Leader", "Associate Cloud Engineer", "Professional Cloud Architect",
        "Professional Cloud Developer", "Professional Data Engineer", "Professional Security Engineer",
        "Professional DevOps Engineer", "Professional Machine Learning Engineer", "Professional Cloud Network Engineer",
        "Professional Cloud Database Engineer", "Professional Collaboration Engineer", "Professional Cloud Architect for Google Workspace",
        "Professional Cloud Security Engineer", "Professional Cloud AI Engineer", "Professional Cloud Application Developer",
        "Professional Cloud Operations Engineer", "Professional Cloud Developer", "Professional Cloud Data Engineer"
    ],
    "alibaba_cloud": [
        "Alibaba Cloud Associate", "Alibaba Cloud Professional", "Big Data",
        "Cloud Computing", "Alibaba Cloud Security Expert", "Alibaba Cloud Data Engineer",
        "Alibaba Cloud Big Data Engineer", "Alibaba Cloud Cloud Architect", "Alibaba Cloud Database Expert",
        "Alibaba Cloud Developer","Alibaba Cloud Solutions Architect", "Alibaba Cloud DevOps Engineer",
        "Alibaba Cloud Machine Learning Engineer", "Alibaba Cloud AI Engineer", "Alibaba Cloud Network Engineer", "Alibaba Cloud Database Administrator",
        "Alibaba Cloud Cloud Security Architect", "Alibaba Cloud Big Data Architect"
    ],
    "hashicorp": ["Terraform Associate", "Vault Associate", "Terraform Advanced Associate",
                  "Vault Advanced Associate", "Consul Associate", "Packer Associate",
                  "Waypoint Associate"
    ],
    "docker": ["Docker Certified Associate (DCA)", "Docker Certified Kubernetes Administrator (DCKA)", "Docker Certified Professional",
               "Docker Certified Expert"
    ],
    "ibm_cloud": [
        "IBM Cloud Solutions Architect", "IBM Cloud Developer", "IBM Cloud Site Reliability Engineer (SRE)",
        "IBM Cloud for SAP", "IBM Cloud for Financial Services", "IBM Cloud Kubernetes Administrator",
        "IBM Cloud Database Administrator", "IBM Cloud Application Developer", "IBM Cloud Continuous Delivery Specialist",
        "IBM Cloud Security Engineer", "IBM Cloud Network Engineer", "IBM Cloud Data Scientist", "IBM Cloud Application Architect",
        "IBM Cloud Developer Foundation"
    ],
    "oracle_cloud": [
        "Oracle Cloud Infrastructure Architect Associate", "Oracle Cloud Infrastructure Architect Professional", "Oracle Cloud Developer",
        "Oracle Cloud Security Specialist", "Oracle Cloud Infrastructure Foundations Associate", "Oracle Cloud Infrastructure Developer Certified Associate",
        "Oracle Cloud Infrastructure Database Certified Associate", "Oracle Cloud Infrastructure Security Certified Associate", "Oracle Cloud Infrastructure Data Science Certified Associate",
        "Oracle Cloud Infrastructure Cloud Operations Certified Associate", "Oracle Cloud Infrastructure Cloud Engineering Certified Associate", "Oracle Cloud Infrastructure Data Management Certified Associate",
        "Oracle Cloud Infrastructure Cloud Applications Certified Associate", "Oracle Cloud Infrastructure Application Development Certified Associate"
    ],
    "huawei_cloud": [
        "Huawei Certified ICT Associate (HCIA)", "Huawei Certified ICT Professional (HCIP)", "Huawei Certified ICT Expert (HCIE)",
        "Huawei Certified Network Associate (HCNA)", "Huawei Certified Network Professional (HCNP)", "Huawei Certified Routing and Switching (HCRS)",
        "Huawei Certified Routing and Switching (HCRS)", "Huawei Certified Cloud Service Developer (HCS-Cloud)", "Huawei Certified Cloud Computing Associate (HCCP)",
        "Huawei Certified AI Engineer (HCAI)", "Huawei Certified Big Data Associate (HCBD)", "Huawei Certified Data Center Facility Associate (HCDFA)",
        "Huawei Certified Cloud Architect (HCCA)", "Huawei Certified Storage Associate (HCSA)", "Huawei Certified Security Associate (HCSA-Security)"
    ],
    "tencent_cloud": [
        "Tencent Cloud Practitioner", "Tencent Cloud Architect", "Tencent Cloud Developer",
        "Tencent Cloud Operations Engineer", "Tencent Cloud Security Engineer", "Tencent Cloud Big Data Engineer",
        "Tencent Cloud AI Engineer", "Tencent Cloud Database Engineer"
    ],
    "openstack": ["Certified OpenStack Administrator", "Certified OpenStack Developer", "Certified OpenStack Architect",
                  "Certified OpenStack Operator"
    ],
    "apache_cloudstack": ["CloudStack Certified Professional", "CloudStack Certified Administrator"],
    "vmware_vsphere": [
        "VMware Certified Professional (VCP)", "VMware Certified Advanced Professional (VCAP)", "VMware Certified Design Expert (VCDX)",
        "VMware Cloud on AWS Master Specialist", "VMware Cloud Management and Automation Master Specialist", "VMware Cloud Foundation Master Specialist",
        "VMware Horizon 8 Master Specialist", "VMware Tanzu Master Specialist"
    ]
}

# Dictionary of topics for each certification and their percentage distributions
exam_topics = {
    "aws": {
        "Cloud Practitioner Foundational": {
            "Cloud Concepts": 24,
            "Security and Compliance": 30,
            "Cloud Technology and Services": 34,
            "Billing, Pricing and Support": 12
        },
        "AI Practitioner Foundational": {
            "AI Concepts and Technologies": 25,
            "Machine Learning Algorithms and Frameworks": 25,
            "Model Deployment and Maintenance": 20,
            "AI Ethics and Responsible AI": 15,
            "AI Solution Design and Implementation": 15
        },
        "Solutions Architect Associate": {
            "Design Resilient Architectures": 30,
            "Design High-Performing Architectures": 28,
            "Design Secure Applications and Architectures": 24,
            "Design Cost-Optimized Architectures": 18
        },
        "Developer Associate": {
            "Development with AWS Services": 30,
            "Deployment and Debugging": 30,
            "Security and Authentication": 20,
            "Refactoring": 10,
            "Monitoring and Troubleshooting": 10
        },
        "SysOps Administrator Associate": {
            "Monitoring, Reporting, and Automation": 20,
            "High Availability, Backup, and Recovery": 20,
            "Deployment, Provisioning, and Automation": 25,
            "Data Management and Security": 20,
            "Incident and Event Response": 15
        },
        "Data Engineer Associate": {
            "Data Engineering Concepts": 20,
            "Data Pipeline Implementation": 25,
            "Data Modeling": 25,
            "Data Security and Compliance": 15,
            "Monitoring and Performance Tuning": 15
        },
        "Machine Learning Engineer Associate": {
            "Machine Learning Fundamentals": 20,
            "Feature Engineering": 25,
            "Model Training and Evaluation": 25,
            "Deployment and Monitoring of Machine Learning Models": 20,
            "Ethics in AI and Machine Learning": 10
        },
        "Solutions Architect Professional": {
            "High-Performance Architecture": 26,
            "Cost and Performance Optimization": 26,
            "Security and Compliance": 24,
            "Migration Planning": 24,
            "Designing for New Solutions": 20
        },
        "Developer Professional": {
            "Development on AWS": 30,
            "Deployment on AWS": 25,
            "Security": 20,
            "Refactoring": 15,
            "Monitoring and Troubleshooting": 10
        },
        "DevOps Engineer Professional": {
            "SDLC Automation": 22,
            "Configuration Management and Infrastructure as Code": 19,
            "Monitoring and Logging": 15,
            "Incident and Event Management": 15,
            "Policies and Standards Automation": 29
        },
        "Advanced Networking Specialty": {
            "Networking Concepts and Design": 30,
            "Network Security": 24,
            "Hybrid Connectivity": 26,
            "AWS Networking Services": 20,
            "Troubleshooting Networking Issues": 20
        },
        "Machine Learning Specialty": {
            "Machine Learning Concepts": 18,
            "Data Engineering": 24,
            "Modeling": 36,
            "Machine Learning Implementation and Operations": 18,
            "Ethics and Security": 4
        },
        "Security Specialty": {
            "Incident Response": 30,
            "Logging and Monitoring": 24,
            "Infrastructure Security": 26,
            "Identity and Access Management": 20,
            "Data Protection": 20
        },
        "Database Specialty": {
            "Database Design": 24,
            "Database Migration": 26,
            "Monitoring and Performance Tuning": 20,
            "Data Security": 20,
            "Backup and Recovery": 20
        },
        "Data Analytics Specialty": {
            "Data Collection and Ingestion": 24,
            "Data Storage and Processing": 24,
            "Data Analysis and Visualization": 32,
            "Data Security and Governance": 12,
            "Machine Learning for Data Analytics": 8
        },
        "Alexa Skill Builder Specialty": {
            "Voice User Interface Design": 18,
            "Skill Development Lifecycle": 24,
            "Skill Monetization and Promotion": 20,
            "Testing and Certification": 20,
            "Analytics and Monitoring": 18
        },
        "Cloud Operations": {
            "Operational Excellence": 30,
            "Security and Compliance": 25,
            "Monitoring and Reporting": 20,
            "Performance Optimization": 25
        },
        "Cloud Economics": {
            "Cost Management": 30,
            "Financial Management": 30,
            "AWS Pricing Models": 20,
            "Optimization Strategies": 20
        },
        "Cloud Migration": {
            "Migration Strategies": 30,
            "AWS Migration Tools": 25,
            "Security during Migration": 20,
            "Post-Migration Optimization": 25
        }
    },
    "azure": {
            "AI Engineer": {
                "AI Solutions": 25,
                "Machine Learning": 25,
                "Natural Language Processing": 20,
                "Computer Vision": 20,
                "Responsible AI": 10
            },
            "Azure Fundamentals": {
                "Cloud Concepts": 30,
                "Core Azure Services": 25,
                "Security, Compliance, and Trust": 20,
                "Azure Pricing, SLA, and Lifecycle": 25
            },
            "Azure Administrator": {
                "Manage Azure subscriptions and resources": 15,
                "Implement storage solutions": 20,
                "Deploy and manage Azure compute resources": 25,
                "Configure and manage virtual networking": 25,
                "Monitor and back up Azure resources": 15
            },
            "Azure Data Scientist": {
                "Data Science Concepts": 25,
                "Data Preparation": 30,
                "Model Training": 25,
                "Model Evaluation": 20
            },
            "Azure Developer": {
                "Develop Azure compute solutions": 25,
                "Develop for Azure storage": 20,
                "Implement Azure security": 25,
                "Monitor, troubleshoot, and optimize Azure solutions": 20,
                "Connect to and consume Azure services": 10
            },
            "Azure Security Engineer": {
                "Manage Identity and Access": 30,
                "Implement Platform Protection": 25,
                "Manage Security Operations": 20,
                "Secure Data and Applications": 25
            },
            "Azure DevOps Engineer": {
                "Implement DevOps development processes": 20,
                "Implement continuous integration": 20,
                "Implement continuous delivery": 25,
                "Implement dependency management": 20,
                "Implement application infrastructure": 15
            },
            "Azure Solutions Architect Associate": {
                "Design for Identity and Security": 25,
                "Design a Data Platform Solution": 20,
                "Design for Business Continuity": 20,
                "Design for Deployment, Migration, and Integration": 20,
                "Design an Infrastructure Strategy": 15
            },
            "Azure Solutions Architect Expert": {
                "Design for Identity and Security": 25,
                "Design for Data Storage": 25,
                "Design for Business Continuity": 20,
                "Design for Deployment and Migration": 20,
                "Design for Infrastructure": 10
            },
            "Azure Data Engineer": {
                "Design and Implement Data Storage": 25,
                "Develop Data Processing": 25,
                "Manage Data Security": 20,
                "Monitor and Optimize Data Solutions": 20,
                "Integrate Data Sources": 10
            },
            "Azure Database Administrator": {
                "Manage SQL Database Instances": 30,
                "Implement Security for Databases": 20,
                "Monitor and Optimize Database Performance": 25,
                "Automate Database Management Tasks": 25
            },
            "Azure AI Fundamentals": {
                "AI Concepts and Principles": 25,
                "Azure AI Services": 25,
                "Machine Learning": 20,
                "Responsible AI": 20,
                "Data Preparation": 10
            },
            "Azure Security Operations Analyst": {
                "Monitor Security with Azure Sentinel": 30,
                "Respond to Security Incidents": 25,
                "Investigate Security Alerts": 20,
                "Implement Security Controls": 25
            },
            "Azure Virtual Desktop": {
                "Plan and Implement an Azure Virtual Desktop Infrastructure": 30,
                "Manage User Environments and Security": 30,
                "Monitor and Optimize Azure Virtual Desktop": 20,
                "Implement Application Virtualization": 20
            },
            "Azure IoT Developer": {
                "Implement IoT Solutions": 25,
                "Provision and Manage Devices": 25,
                "Implement Data Solutions": 20,
                "Secure IoT Solutions": 20,
                "Monitor IoT Solutions": 10
            },
            "Azure Cosmos DB Developer": {
                "Develop for Cosmos DB": 25,
                "Manage Data in Cosmos DB": 30,
                "Implement Security and Compliance": 25,
                "Optimize Performance": 20
            },
            "Azure AI Engineer Associate": {
                "Analyze Solution Requirements": 25,
                "Implement Computer Vision Solutions": 25,
                "Implement Natural Language Processing Solutions": 20,
                "Implement Conversational AI Solutions": 20,
                "Implement Responsible AI": 10
            },
            "Azure Data Analyst Associate": {
                "Prepare Data for Analysis": 25,
                "Model Data": 25,
                "Visualize Data": 25,
                "Deploy Solutions for Consumption": 25
            },
            "Azure Security Architect": {
                "Design Security for Identity and Access": 30,
                "Design Security for Data and Applications": 25,
                "Design Security for Infrastructure": 25,
                "Implement Security Governance": 20
            },
            "Azure Solutions Architect": {
                "Design for Identity and Security": 25,
                "Design a Data Platform Solution": 20,
                "Design for Business Continuity": 20,
                "Design for Deployment, Migration, and Integration": 20,
                "Design an Infrastructure Strategy": 15
            },
            "Azure Certified Data Scientist Associate": {
                "Data Science Concepts": 25,
                "Data Preparation": 30,
                "Model Training": 25,
                "Model Evaluation": 20
            },
            "Azure Certified Cloud Data Engineer Associate": {
                "Design and Implement Data Storage": 25,
                "Develop Data Processing": 25,
                "Manage Data Security": 20,
                "Monitor and Optimize Data Solutions": 20,
                "Integrate Data Sources": 10
            }
        },
    "gcp": {
        "Cloud Digital Leader": {
            "Cloud Concepts": 30,
            "Google Cloud Products and Services": 30,
            "Security and Compliance": 20,
            "Digital Transformation": 20
        },
        "Associate Cloud Engineer": {
            "Setting Up a Cloud Solution Environment": 20,
            "Planning and Configuring a Cloud Solution": 30,
            "Deploying and Implementing a Cloud Solution": 30,
            "Ensuring Successful Operation of a Cloud Solution": 20
        },
        "Professional Cloud Architect": {
            "Designing and Planning Cloud Solution Architecture": 30,
            "Managing and Provisioning Cloud Solutions": 30,
            "Security and Compliance": 20,
            "Analyzing and Optimizing Technical and Business Processes": 20
        },
        "Professional Cloud Developer": {
            "Application Development": 30,
            "Continuous Integration and Delivery": 30,
            "Security": 20,
            "Monitoring and Troubleshooting": 20
        },
        "Professional Data Engineer": {
            "Data Engineering Concepts": 25,
            "Building Data Processing Systems": 25,
            "Data Analysis and Visualization": 25,
            "Data Security and Compliance": 25
        },
        "Professional Security Engineer": {
            "Security Design and Architecture": 30,
            "Security Operations and Incident Response": 30,
            "Compliance and Risk Management": 20,
            "Identity and Access Management": 20
        },
        "Professional DevOps Engineer": {
            "Site Reliability Engineering": 30,
            "Continuous Delivery and Automation": 30,
            "Monitoring and Logging": 20,
            "Incident Management": 20
        },
        "Professional Machine Learning Engineer": {
            "Machine Learning Concepts": 30,
            "Data Preparation and Processing": 30,
            "Model Training and Evaluation": 20,
            "Model Deployment and Monitoring": 20
        },
        "Professional Cloud Network Engineer": {
            "Network Design and Implementation": 30,
            "Network Security": 30,
            "Network Management and Operations": 20,
            "Network Troubleshooting": 20
        },
        "Professional Cloud Database Engineer": {
            "Database Design": 30,
            "Database Management": 30,
            "Database Security": 20,
            "Performance Optimization": 20
        },
        "Professional Collaboration Engineer": {
            "Collaboration Solutions": 30,
            "Security and Compliance": 30,
            "User Management": 20,
            "Deployment and Integration": 20
        },
        "Professional Cloud Architect for Google Workspace": {
            "Google Workspace Architecture": 30,
            "Security and Compliance": 30,
            "User Management": 20,
            "Deployment Strategies": 20
        },
        "Professional Cloud Security Engineer": {
            "Security Design and Architecture": 30,
            "Incident Response and Recovery": 30,
            "Compliance and Risk Management": 20,
            "Identity and Access Management": 20
        },
        "Professional Cloud AI Engineer": {
            "AI Concepts and Frameworks": 30,
            "Data Preparation and Processing": 30,
            "Model Training and Evaluation": 20,
            "Deployment and Monitoring": 20
        },
        "Professional Cloud Application Developer": {
            "Application Development": 30,
            "Security": 20,
            "Deployment and Operations": 30,
            "Monitoring and Troubleshooting": 20
        },
        "Professional Cloud Operations Engineer": {
            "Operational Excellence": 30,
            "Monitoring and Logging": 30,
            "Incident Management": 20,
            "Performance Optimization": 20
        },
        "Professional Cloud Data Engineer": {
            "Data Engineering Concepts": 25,
            "Data Processing Systems": 25,
            "Data Security and Compliance": 25,
            "Data Analysis and Visualization": 25
        }
    },
    "alibaba_cloud": {
        "Alibaba Cloud Associate": {
            "Cloud Concepts": 30,
            "Core Alibaba Cloud Services": 30,
            "Security and Compliance": 20,
            "Billing and Pricing": 20
        },
        "Alibaba Cloud Professional": {
            "Architecture Design": 25,
            "Service Management": 25,
            "Performance Optimization": 25,
            "Security and Compliance": 25
        },
        "Big Data": {
            "Data Processing": 20,
            "Data Storage": 20,
            "Data Analysis": 25,
            "Data Visualization": 20,
            "Big Data Security": 15
        },
        "Cloud Computing": {
            "Cloud Computing Fundamentals": 25,
            "Virtualization": 25,
            "Storage Solutions": 25,
            "Cloud Security": 25
        },
        "Alibaba Cloud Security Expert": {
            "Security Architecture": 30,
            "Risk Assessment": 25,
            "Incident Response": 25,
            "Compliance and Governance": 20
        },
        "Alibaba Cloud Data Engineer": {
            "Data Processing and Transformation": 30,
            "Database Management": 25,
            "Data Integration": 25,
            "Data Security": 20
        },
        "Alibaba Cloud Big Data Engineer": {
            "Big Data Technologies": 25,
            "Data Processing": 30,
            "Data Storage Solutions": 25,
            "Big Data Security": 20
        },
        "Alibaba Cloud Cloud Architect": {
            "Architectural Design Principles": 30,
            "System Integration": 25,
            "Scalability and Performance": 25,
            "Cost Optimization": 20
        },
        "Alibaba Cloud Database Expert": {
            "Database Design": 25,
            "Database Management": 30,
            "Data Migration": 20,
            "Performance Optimization": 25
        },
        "Alibaba Cloud Developer": {
            "Development Practices": 30,
            "API Management": 25,
            "Application Security": 20,
            "Deployment and Monitoring": 25
        },
        "Alibaba Cloud Solutions Architect": {
            "Architectural Design": 30,
            "Cost Management": 25,
            "Performance Optimization": 25,
            "Security and Compliance": 20
        },
        "Alibaba Cloud DevOps Engineer": {
            "CI/CD Practices": 30,
            "Infrastructure as Code": 25,
            "Monitoring and Logging": 20,
            "Incident Management": 25
        },
        "Alibaba Cloud Machine Learning Engineer": {
            "Machine Learning Fundamentals": 25,
            "Model Training": 30,
            "Model Evaluation": 25,
            "Deployment of Machine Learning Models": 20
        },
        "Alibaba Cloud AI Engineer": {
            "AI Concepts": 30,
            "Machine Learning Algorithms": 25,
            "Natural Language Processing": 25,
            "AI Ethics": 20
        },
        "Alibaba Cloud Network Engineer": {
            "Networking Concepts": 30,
            "Network Security": 25,
            "Cloud Network Architecture": 25,
            "Monitoring and Troubleshooting": 20
        },
        "Alibaba Cloud Database Administrator": {
            "Database Management": 30,
            "Backup and Recovery": 25,
            "Performance Tuning": 25,
            "Security Management": 20
        },
        "Alibaba Cloud Cloud Security Architect": {
            "Security Architecture": 30,
            "Risk Management": 25,
            "Incident Response Planning": 25,
            "Compliance Standards": 20
        },
        "Alibaba Cloud Big Data Architect": {
            "Big Data Architecture": 30,
            "Data Processing Frameworks": 25,
            "Data Governance": 25,
            "Performance Optimization": 20
        }
    },
    "hashicorp": {
        "Terraform Associate": {
            "Understand Infrastructure as Code (IaC)": 20,
            "Use Terraform to Create and Manage Infrastructure": 25,
            "Manage Terraform State": 20,
            "Work with Terraform Modules": 20,
            "Implement Terraform Workspaces": 15
        },
        "Vault Associate": {
            "Understand Vault Architecture": 25,
            "Secure Secrets Management": 25,
            "Manage Identity and Access Management (IAM)": 20,
            "Work with Secrets Engines": 20,
            "Implement Audit Logging": 10
        },
        "Terraform Advanced Associate": {
            "Advanced Terraform Configuration": 30,
            "Terraform State Management": 25,
            "Terraform Module Design": 25,
            "Use Terraform with CI/CD": 20
        },
        "Vault Advanced Associate": {
            "Advanced Vault Configuration": 30,
            "Implement Dynamic Secrets": 25,
            "Manage Encryption and Key Management": 25,
            "Integrate Vault with Other Tools": 20
        },
        "Consul Associate": {
            "Understand Service Mesh Concepts": 25,
            "Deploy and Manage Consul Clusters": 25,
            "Service Discovery and Health Checking": 25,
            "Consul Connect for Service-to-Service Communication": 25
        },
        "Packer Associate": {
            "Understand Packer Basics": 30,
            "Create and Manage Packer Templates": 25,
            "Use Provisioners and Post-Processors": 25,
            "Integrate Packer with Other Tools": 20
        },
        "Waypoint Associate": {
            "Understand Application Delivery Concepts": 30,
            "Deploy Applications with Waypoint": 25,
            "Manage Application Configurations": 25,
            "Integrate Waypoint with Other Tools": 20
        }
    },
    "docker": {
        "Docker Certified Associate (DCA)": {
            "Docker Overview": 20,
            "Image Creation, Management, and Registry": 25,
            "Networking": 15,
            "Orchestration": 20,
            "Security": 10,
            "Storage and Volumes": 10
        },
        "Docker Certified Kubernetes Administrator (DCKA)": {
            "Kubernetes Architecture": 20,
            "Installation and Configuration": 25,
            "Workloads and Scheduling": 20,
            "Services and Networking": 15,
            "Storage": 10,
            "Monitoring and Logging": 10
        },
        "Docker Certified Professional": {
            "Docker Basics": 25,
            "Image Management and Networking": 25,
            "Container Orchestration": 20,
            "Application Deployment and Scaling": 15,
            "Security Best Practices": 15
        },
        "Docker Certified Expert": {
            "Advanced Docker Concepts": 30,
            "Troubleshooting Docker Environments": 25,
            "Performance Tuning": 25,
            "Integration with CI/CD": 20
        }
    },
    "ibm_cloud": {
        "IBM Cloud Solutions Architect": {
            "Architecture Design": 30,
            "Cloud Application Development": 25,
            "Security and Compliance": 20,
            "Deployment Models": 15,
            "Cost Management": 10
        },
        "IBM Cloud Developer": {
            "Cloud Application Development": 30,
            "API Integration": 25,
            "Microservices Architecture": 20,
            "DevOps Practices": 15,
            "Cloud Security": 10
        },
        "IBM Cloud Site Reliability Engineer (SRE)": {
            "Service Reliability": 30,
            "Incident Management": 25,
            "Monitoring and Observability": 20,
            "Automation": 15,
            "Performance Optimization": 10
        },
        "IBM Cloud for SAP": {
            "SAP Architecture on Cloud": 25,
            "Deployment Strategies": 25,
            "Security and Compliance": 20,
            "Performance Optimization": 15,
            "Cost Management": 15
        },
        "IBM Cloud for Financial Services": {
            "Financial Services Compliance": 30,
            "Data Security": 25,
            "Application Development": 20,
            "Regulatory Requirements": 15,
            "Cloud Migration": 10
        },
        "IBM Cloud Kubernetes Administrator": {
            "Kubernetes Architecture": 25,
            "Installation and Configuration": 20,
            "Workloads and Scheduling": 20,
            "Networking": 15,
            "Storage": 10,
            "Monitoring and Logging": 10
        },
        "IBM Cloud Database Administrator": {
            "Database Design and Management": 30,
            "Performance Tuning": 25,
            "Security Best Practices": 20,
            "Backup and Recovery": 15,
            "Database Migration": 10
        },
        "IBM Cloud Application Developer": {
            "Application Development": 30,
            "API Development": 25,
            "Microservices": 20,
            "DevOps Integration": 15,
            "Security Practices": 10
        },
        "IBM Cloud Continuous Delivery Specialist": {
            "Continuous Integration/Continuous Deployment": 30,
            "Automation": 25,
            "Monitoring and Logging": 20,
            "Collaboration Tools": 15,
            "Security in CI/CD": 10
        },
        "IBM Cloud Security Engineer": {
            "Security Architecture": 30,
            "Identity and Access Management": 25,
            "Data Security": 20,
            "Incident Response": 15,
            "Compliance Management": 10
        },
        "IBM Cloud Network Engineer": {
            "Network Design": 30,
            "Security in Networking": 25,
            "Load Balancing": 20,
            "VPN Configuration": 15,
            "Monitoring Network Performance": 10
        },
        "IBM Cloud Data Scientist": {
            "Data Analysis": 30,
            "Machine Learning": 25,
            "Data Visualization": 20,
            "Big Data Technologies": 15,
            "Statistical Analysis": 10
        },
        "IBM Cloud Application Architect": {
            "Application Design Principles": 30,
            "Microservices Architecture": 25,
            "Security Best Practices": 20,
            "Scalability and Performance": 15,
            "Cost Management": 10
        },
        "IBM Cloud Developer Foundation": {
            "Cloud Fundamentals": 30,
            "Application Development Basics": 25,
            "DevOps Concepts": 20,
            "API Management": 15,
            "Cloud Security Fundamentals": 10
        }
    },
    "oracle_cloud": {
        "Oracle Cloud Infrastructure Architect Associate": {
            "Cloud Concepts": 25,
            "Core Services": 30,
            "Security and Compliance": 20,
            "Architecture Design": 15,
            "Cost Management": 10
        },
        "Oracle Cloud Infrastructure Architect Professional": {
            "Architectural Patterns": 30,
            "High Availability and Disaster Recovery": 25,
            "Performance Tuning": 20,
            "Security Best Practices": 15,
            "Cost Optimization": 10
        },
        "Oracle Cloud Developer": {
            "Application Development": 30,
            "APIs and Microservices": 25,
            "Database Management": 20,
            "Security Practices": 15,
            "Deployment Strategies": 10
        },
        "Oracle Cloud Security Specialist": {
            "Identity and Access Management": 30,
            "Data Security": 25,
            "Compliance and Governance": 20,
            "Incident Response": 15,
            "Security Architecture": 10
        },
        "Oracle Cloud Infrastructure Foundations Associate": {
            "Cloud Concepts": 30,
            "Core Services Overview": 25,
            "Security and Compliance Basics": 20,
            "Pricing and Billing": 15,
            "Support and Documentation": 10
        },
        "Oracle Cloud Infrastructure Developer Certified Associate": {
            "Development with OCI": 30,
            "APIs and SDKs": 25,
            "Database Integration": 20,
            "Deployment Strategies": 15,
            "Security Practices": 10
        },
        "Oracle Cloud Infrastructure Database Certified Associate": {
            "Database Management": 30,
            "Performance Tuning": 25,
            "Backup and Recovery": 20,
            "Security Best Practices": 15,
            "Data Migration": 10
        },
        "Oracle Cloud Infrastructure Security Certified Associate": {
            "Security Architecture": 30,
            "Identity and Access Management": 25,
            "Data Protection": 20,
            "Compliance Management": 15,
            "Incident Response": 10
        },
        "Oracle Cloud Infrastructure Data Science Certified Associate": {
            "Data Science Concepts": 30,
            "Machine Learning": 25,
            "Data Visualization": 20,
            "Data Engineering": 15,
            "Deployment of Models": 10
        },
        "Oracle Cloud Infrastructure Cloud Operations Certified Associate": {
            "Operational Excellence": 30,
            "Monitoring and Reporting": 25,
            "Incident Management": 20,
            "Security Best Practices": 15,
            "Cost Management": 10
        },
        "Oracle Cloud Infrastructure Cloud Engineering Certified Associate": {
            "Cloud Architecture": 30,
            "Infrastructure Management": 25,
            "Network Design": 20,
            "Security Practices": 15,
            "Cost Optimization": 10
        },
        "Oracle Cloud Infrastructure Data Management Certified Associate": {
            "Data Management Principles": 30,
            "Data Governance": 25,
            "Data Security": 20,
            "Data Migration": 15,
            "Backup and Recovery": 10
        },
        "Oracle Cloud Infrastructure Cloud Applications Certified Associate": {
            "Cloud Application Fundamentals": 30,
            "Integration Strategies": 25,
            "User Experience Design": 20,
            "Security Best Practices": 15,
            "Deployment Strategies": 10
        },
        "Oracle Cloud Infrastructure Application Development Certified Associate": {
            "Application Development Lifecycle": 30,
            "APIs and Microservices": 25,
            "Database Integration": 20,
            "Security Practices": 15,
            "Deployment and Monitoring": 10
        }
    },
    "huawei_cloud": {
        "Huawei Certified ICT Associate (HCIA)": {
            "Fundamentals of ICT": 25,
            "Network Technologies": 30,
            "Cloud Computing Basics": 20,
            "Cybersecurity Concepts": 15,
            "Basic Troubleshooting": 10
        },
        "Huawei Certified ICT Professional (HCIP)": {
            "Advanced Networking": 30,
            "Cloud Architecture": 25,
            "Security Technologies": 20,
            "Service Quality Management": 15,
            "Project Management Basics": 10
        },
        "Huawei Certified ICT Expert (HCIE)": {
            "Expert-level Networking": 35,
            "Advanced Cloud Solutions": 30,
            "Service Optimization": 20,
            "Security Practices": 10,
            "Best Practices": 5
        },
        "Huawei Certified Network Associate (HCNA)": {
            "Networking Fundamentals": 30,
            "Basic Routing and Switching": 30,
            "Network Security Basics": 20,
            "Troubleshooting Techniques": 15,
            "Basic Network Management": 5
        },
        "Huawei Certified Network Professional (HCNP)": {
            "Advanced Routing and Switching": 35,
            "Network Design Principles": 25,
            "Network Security Practices": 20,
            "Service Quality Assurance": 10,
            "Management Tools": 10
        },
        "Huawei Certified Routing and Switching (HCRS)": {
            "Routing Protocols": 30,
            "Switching Techniques": 25,
            "Network Security": 20,
            "Performance Optimization": 15,
            "Troubleshooting": 10
        },
        "Huawei Certified Cloud Service Developer (HCS-Cloud)": {
            "Cloud Development Fundamentals": 30,
            "APIs and Microservices": 25,
            "Deployment Techniques": 20,
            "Database Integration": 15,
            "Security Practices": 10
        },
        "Huawei Certified Cloud Computing Associate (HCCP)": {
            "Cloud Concepts": 30,
            "Virtualization Technologies": 25,
            "Service Management": 20,
            "Basic Security Measures": 15,
            "Cost Management": 10
        },
        "Huawei Certified AI Engineer (HCAI)": {
            "AI Fundamentals": 30,
            "Machine Learning": 25,
            "Data Processing": 20,
            "Model Deployment": 15,
            "AI Ethics": 10
        },
        "Huawei Certified Big Data Associate (HCBD)": {
            "Big Data Concepts": 30,
            "Data Processing Technologies": 25,
            "Data Storage Solutions": 20,
            "Basic Data Analytics": 15,
            "Security and Compliance": 10
        },
        "Huawei Certified Data Center Facility Associate (HCDFA)": {
            "Data Center Fundamentals": 30,
            "Infrastructure Management": 25,
            "Energy Efficiency Practices": 20,
            "Security Measures": 15,
            "Disaster Recovery": 10
        },
        "Huawei Certified Cloud Architect (HCCA)": {
            "Cloud Architecture Design": 35,
            "Service Deployment Strategies": 25,
            "Security Best Practices": 20,
            "Cost Optimization": 10,
            "Project Management": 10
        },
        "Huawei Certified Storage Associate (HCSA)": {
            "Storage Technologies": 30,
            "Data Protection Strategies": 25,
            "Performance Optimization": 20,
            "Basic Troubleshooting": 15,
            "Management Tools": 10
        },
        "Huawei Certified Security Associate (HCSA-Security)": {
            "Security Fundamentals": 30,
            "Risk Management": 25,
            "Security Architecture": 20,
            "Incident Response": 15,
            "Compliance Practices": 10
        }
    },
    "tencent_cloud": {
        "Tencent Cloud Practitioner": {
            "Cloud Computing Basics": 30,
            "Tencent Cloud Services Overview": 25,
            "Networking Concepts": 20,
            "Basic Security Principles": 15,
            "Customer Support": 10
        },
        "Tencent Cloud Architect": {
            "Architectural Design Principles": 30,
            "Cloud Solution Implementation": 25,
            "Security Best Practices": 20,
            "Cost Management": 15,
            "Performance Optimization": 10
        },
        "Tencent Cloud Developer": {
            "Development Fundamentals": 30,
            "API Integration": 25,
            "Microservices Architecture": 20,
            "Cloud Deployment": 15,
            "Version Control Practices": 10
        },
        "Tencent Cloud Operations Engineer": {
            "Operations Management": 30,
            "Monitoring and Alerting": 25,
            "Incident Management": 20,
            "Automation Techniques": 15,
            "Capacity Planning": 10
        },
        "Tencent Cloud Security Engineer": {
            "Security Fundamentals": 30,
            "Risk Assessment and Management": 25,
            "Data Protection Techniques": 20,
            "Compliance Requirements": 15,
            "Incident Response": 10
        },
        "Tencent Cloud Big Data Engineer": {
            "Big Data Concepts": 30,
            "Data Processing Techniques": 25,
            "Data Storage Solutions": 20,
            "Basic Analytics Skills": 15,
            "Security and Compliance": 10
        },
        "Tencent Cloud AI Engineer": {
            "AI and Machine Learning Basics": 30,
            "Data Preparation Techniques": 25,
            "Model Training and Evaluation": 20,
            "Deployment Strategies": 15,
            "Ethical Considerations in AI": 10
        },
        "Tencent Cloud Database Engineer": {
            "Database Fundamentals": 30,
            "Database Design Principles": 25,
            "Performance Tuning Techniques": 20,
            "Backup and Recovery Strategies": 15,
            "Security Best Practices": 10
        }
    },
    "apache_cloudstack": {
        "CloudStack Certified Professional": {
            "Cloud Architecture Fundamentals": 25,
            "Installation and Configuration": 25,
            "Networking and Security": 20,
            "Storage Management": 15,
            "Troubleshooting and Maintenance": 15
        },
        "CloudStack Certified Administrator": {
            "CloudStack Administration": 30,
            "Resource Management": 25,
            "Monitoring and Reporting": 20,
            "User Management and Security": 15,
            "Backup and Recovery": 10
        }
    },
    "vmware_vsphere": {
        "VMware Certified Professional (VCP)": {
            "vSphere Architecture": 30,
            "Installation and Configuration": 25,
            "Resource Management": 20,
            "Monitoring and Performance Tuning": 15,
            "Backup and Recovery": 10
        },
        "VMware Certified Advanced Professional (VCAP)": {
            "Advanced vSphere Design": 30,
            "Advanced Installation and Configuration": 25,
            "Resource Management and Optimization": 20,
            "Monitoring and Performance Management": 15,
            "Advanced Troubleshooting": 10
        },
        "VMware Certified Design Expert (VCDX)": {
            "Enterprise Architecture": 25,
            "Design Principles and Best Practices": 30,
            "Design Security and Compliance": 20,
            "Implementation and Migration Planning": 15,
            "Operational Management": 10
        },
        "VMware Cloud on AWS Master Specialist": {
            "Architecture and Design": 30,
            "Deployment and Configuration": 25,
            "Management and Operations": 20,
            "Security and Compliance": 15,
            "Networking and Integration": 10
        },
        "VMware Cloud Management and Automation Master Specialist": {
            "Cloud Management Fundamentals": 30,
            "Automation with vRealize Orchestrator": 25,
            "Monitoring and Performance Management": 20,
            "Capacity Management": 15,
            "Security and Compliance": 10
        },
        "VMware Cloud Foundation Master Specialist": {
            "Cloud Foundation Architecture": 30,
            "Deployment and Configuration": 25,
            "Management and Operations": 20,
            "Monitoring and Performance Tuning": 15,
            "Troubleshooting and Maintenance": 10
        },
        "VMware Horizon 8 Master Specialist": {
            "Horizon Architecture and Design": 30,
            "Deployment and Configuration": 25,
            "User Environment Management": 20,
            "Monitoring and Performance Management": 15,
            "Troubleshooting": 10
        },
        "VMware Tanzu Master Specialist": {
            "Kubernetes Fundamentals": 30,
            "Deployment and Management of Tanzu": 25,
            "Monitoring and Troubleshooting": 20,
            "Integration with CI/CD Tools": 15,
            "Security and Compliance": 10
        }
    }
    # Add other CSPs and their topics here...
}

# Specify intents for the bot
intents = discord.Intents.default()
intents.messages = True  # Enable the message intent
intents.guilds = True  # Enable guild intents
intents.members = True  # Enable member intents if you need to interact with members
intents.message_content = True  # Enable content intent for message content

# Command prefix
bot = commands.Bot(command_prefix="stellar_", intents=intents)

# Structure to hold active quizzes
active_quizzes = {}

# Structure to hold active user selections
user_data = {}

# JSON file to store user quiz results
json_file = 'quiz_results.json'

# Initialize JSON file if it doesn't exist
if not os.path.exists(json_file):
    with open(json_file, 'w') as file:
        json.dump({}, file)


# Function to load data from JSON
def load_json():
    with open(json_file, 'r') as file:
        return json.load(file)


# Function to save data to JSON
def save_json(data):
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

CACHE_FILE = 'exam_topics_cache.json'
EXPIRY_DAYS = 30  # Number of days after which to refresh the cache

# Function to load the cache from a JSON file
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

# Function to save the cache to a JSON file
def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)

# Function to check if cached data is expired (older than 30 days)
def is_cache_expired(cached_entry):
    if 'timestamp' not in cached_entry:
        return True  # If there's no timestamp, consider the cache expired

    cache_time = datetime.strptime(cached_entry['timestamp'], "%Y-%m-%d")
    return datetime.now() - cache_time > timedelta(days=EXPIRY_DAYS)


# Function to get exam topics and services (with caching and expiry logic)
async def get_exam_topics(exam):
    # Fetch the selected CSP based on the exam
    selected_csp = next((csp for csp, exams in csp_certifications.items() if exam in exams), None)

    if selected_csp is None:
        print(f"No CSP found for exam: {exam}")
        return {}

    cache = load_cache()

    # Check if the exam already exists in the cache and if it's still valid (not expired)
    if selected_csp in cache and exam in cache[selected_csp] and not is_cache_expired(cache[selected_csp][exam]):
        print(f"Cache hit for exam: {exam} under CSP: {selected_csp}")
        return cache[selected_csp][exam]['data']['topics']  # Return only the topics part

    # If cache is expired or not found, fetch new data from GPT
    print(f"Fetching new data for exam: {exam} under CSP: {selected_csp}")
    prompt = (f"""
        Provide a detailed and complete list of topics covered in the {exam} certification exam for {selected_csp}, 
        along with their corresponding percentage distribution and all web services linked with each topic. 
        Include every relevant service that is part of each topic, without skipping even a single topic or a single service. 
        Make sure every single related topic and service is mentioned and avoid using terms like 'etc.'

        The list should follow this specific format:

        1. Main Topic Name (percentage%)
           - List of services related to this topic, each starting with a hyphen (-) and no additional text or numbering.

        Ensure that:
        - Each main topic is numbered, followed by the topic name and the percentage in parentheses (e.g., 1. Cloud Concepts (28%)).
        - Each main topic has a corresponding list of related services, and each service starts with a hyphen (-) followed by the service name, with no other punctuation or symbols.
        - Do not skip any topics or services, and avoid using terms like 'etc.'
        - Ensure every topic and service is on its own line and follows the structure above. Avoid any extraneous information or invalid formatting.
    """)

    # Make the OpenAI API call
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700
    )

    topics_data = response['choices'][0]['message']['content'].strip()
    print("Raw GPT response:", topics_data)
    topics = {}

    # Split the response into lines and parse it
    lines = topics_data.split('\n')
    current_topic = None
    for line in lines:
        # Check if the line matches a main topic format (e.g., 1. Cloud Concepts (28%))
        main_topic_match = re.match(r'^\d+\.\s*(.+?)\s*\((\d+)%\)', line)
        if main_topic_match:
            current_topic = main_topic_match.group(1).strip()
            percentage = int(main_topic_match.group(2).strip())
            topics[current_topic] = {'percentage': percentage, 'services': []}
        elif current_topic and line.strip().startswith('-'):
            # If the line starts with '-', it's a service
            service_name = line.strip().lstrip('- ').strip()
            if service_name:  # Only add non-empty service names
                topics[current_topic]['services'].append(service_name)

    # If no valid topics were found
    if not topics:
        print("No valid topics found. Returning empty dictionary.")
        return {}

    # Update cache with the new data in the desired format
    if selected_csp not in cache:
        cache[selected_csp] = {}  # Create a new entry for the CSP if it doesn't exist

    # Store the topics under the selected CSP and exam
    cache[selected_csp][exam] = {
        'data': {
            'exam': exam,
            'topics': topics
        },
        'timestamp': datetime.now().strftime("%Y-%m-%d")
    }
    save_cache(cache)

    print(f"Parsed topics: {topics}")
    return topics

# Function to generate a question based on a service
async def generate_gpt_question(service, csp):
    messages = [
        {
            "role": "user",
            "content": f"""
                    Create a multiple-choice question about the {service} web service related to {csp} that resembles an actual certification exam question. 
                    - The question should be realistic, scenario-based, and related to practical applications of the {service} web service.
                    - Provide 4 distinct answer choices where one is the correct answer, and the other three are plausible but incorrect (common misconceptions or related services).
                    - Avoid including the service name in the answer choices unless necessary.
                    - Use industry-specific terminology and align the question with current best practices for using {service} in a real-world {csp} environment.
                    - Do not include any prefixes like 'Question:', 'Scenario:', or similar. Just write the question and choices directly.
                    - Clearly specify the correct answer at the end.
                """
        }
    ]
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150
    )

    # Check if the response is valid
    text = response['choices'][0]['message']['content'].strip()
    question_data = re.split('\n+', text)

    # Debugging information
    print("Generated question data:", question_data)

    # Ensure the question_data has enough elements
    if len(question_data) < 6:
        print("Unexpected response format from OpenAI API: ", question_data)
        raise ValueError("The response does not contain enough data.")

    # Combine the question and scenario into one line
    question = question_data[0]  # The first line should be the scenario and question
    choices = question_data[1:5]  # The next four lines are the answer choices
    correct_answer = question_data[5]  # The last line is the correct answer

    # Validate choices length
    if len(choices) < 4:
        print("Insufficient choices generated, returning default values.")
        choices = ["Choice 1", "Choice 2", "Choice 3", "Choice 4"]  # Placeholder choices

    return question, choices, correct_answer

# Function to generate a quiz based on user selection
async def generate_quiz(exam, num_questions, user_id, is_custom=False):
    quiz_questions = []

    # Load cache at the start of the function
    cache = load_cache()

    # Fetch the selected CSP based on the exam
    selected_csp = next((csp for csp, exams in csp_certifications.items() if exam in exams), None)

    if is_custom:
        # If custom, fetch the custom topics from the cache
        cached_topics = cache.get('data', {}).get('topics', {})
        custom_topics = list(cached_topics.keys())  # Get all topics from the cache

        # Generate questions for each custom topic
        for topic in custom_topics:
            num_topic_questions = num_questions // len(custom_topics)  # Distribute questions evenly

            for _ in range(num_topic_questions):
                service = random.choice(cached_topics[topic]['services'])  # Select random service
                question, choices, answer = await generate_gpt_question(service, selected_csp)  # Pass csp
                quiz_questions.append({"question": question, "choices": choices, "answer": answer, "topic": topic})

        # Check if there are any remaining questions to fill
        remaining_questions = num_questions - len(quiz_questions)
        if remaining_questions > 0:
            all_topics = custom_topics  # Use only the custom topics for remaining questions
            random_topics = random.choices(all_topics, k=remaining_questions)

            for topic in random_topics:
                service = random.choice(cached_topics[topic]['services'])  # Select random service
                question, choices, answer = await generate_gpt_question(service, selected_csp)  # Pass csp
                quiz_questions.append({"question": question, "choices": choices, "answer": answer, "topic": topic})
    else:
        # For standard exams, get topics and their percentages
        topics = await get_exam_topics(exam)
        print("Got topics")
        print(topics)
        print(f"Exam: {exam}")

        # Store topic percentages temporarily
        topic_percentages = {}
        for topic, info in topics.items():
            num_topic_questions = 0  # Initialize variable to ensure it's defined

            if isinstance(info, dict) and "percentage" in info:
                percentage = info["percentage"]
                if not isinstance(percentage, (int, float)):  # Ensure percentage is a number
                    print(f"Invalid percentage value for topic '{topic}': {percentage}. Expected a number.")
                    continue

                num_topic_questions = int((percentage / 100) * num_questions)
                topic_percentages[topic] = {
                    'percentage': percentage,  # Store the topic percentage
                    'num_questions': num_topic_questions  # Store the number of questions for this topic
                }
                print(f"Topic: {topic}, Percent: {percentage}, Questions: {num_topic_questions}")

                # Generate questions based on the calculated num_topic_questions
                for _ in range(num_topic_questions):
                    service = random.choice(info['services'])  # Select random service
                    question, choices, answer = await generate_gpt_question(service, selected_csp)  # Pass csp
                    quiz_questions.append({"question": question, "choices": choices, "answer": answer, "topic": topic})

            else:
                print(f"Invalid info structure for topic: {topic}. Expected a dict with 'percentage'.")

        # Fill remaining questions randomly from the topics
        remaining_questions = num_questions - len(quiz_questions)
        if remaining_questions > 0:
            all_topics = list(topics.keys())
            random_topics = random.choices(all_topics, k=remaining_questions)

            for topic in random_topics:
                service = random.choice(topics[topic]['services'])  # Select random service
                question, choices, answer = await generate_gpt_question(service, selected_csp)  # Pass csp
                quiz_questions.append({"question": question, "choices": choices, "answer": answer, "topic": topic})

    random.shuffle(quiz_questions)  # Shuffle to mix topics

    # Store topic percentages in user's data
    user_data[user_id]["topic_percentages"] = topic_percentages if not is_custom else {}

    # Store CSP and Certification in user data
    user_data[user_id]["csp_certification"] = {
        "csp": "custom" if is_custom else "standard",
        "cert": exam  # Store the exam name as certification
    }

    return quiz_questions

# Guide_command to explain bot functionality
@bot.command(name="guide")
async def guide(ctx):
    guide_message = (
        "Greetings, aspiring cloud expert! 🌥️ I'm Stellar, your quiz companion. Here's how to use me:\n"
        "1. Use `stellar_sq` to begin your journey.\n"
        "2. Select your Cloud Service Provider (CSP) from the list. To achieve this, you must type `stellar_select <number_of_selected_choice>`.\n"
        "3. Choose the certification you're preparing for. For this purpose, type `stellar_select <number_of_selected_choice>`.\n"
        "4. Specify how many questions you'd like (1-120). To do so, type `stellar_select <selected_number>`.\n"
        "5. Answer each question by typing the number of your answer choice in this format: `stellar_ans <number_of_selected_choice>`.\n"
        "6. At the end, I'll reveal your score and a detailed breakdown of your answers.\n"
        "Just call my name, and I'll be here to assist you!"
    )
    await ctx.send(guide_message)

@bot.command(name="sq")
async def start_quiz(ctx):
    """Start the quiz by asking the user to select a CSP."""
    await ctx.send("Welcome to the quiz! Please select your cloud provider:\n"
                   + "\n".join([f"{i + 1}. {csp.upper()}" for i, csp in enumerate(csp_certifications.keys())]))
    user_data[ctx.author.id] = {"step": "csp_selection"}


@bot.command(name="select")
async def select(ctx, *, selection):
    user_id = ctx.author.id
    if user_id not in user_data or "step" not in user_data[user_id]:
        await ctx.send("You have not started the quiz process. Use `stellar_sq` to begin.")
        return

    step = user_data[user_id]["step"]

    # Step 1: Handle CSP selection
    if step == "csp_selection":
        try:
            selection = int(selection)
            if 1 <= selection <= len(csp_certifications):
                selected_csp = list(csp_certifications.keys())[selection - 1]
                user_data[user_id]["csp"] = selected_csp
                user_data[user_id]["step"] = "cert_selection"

                # Show certifications available for the selected CSP
                cert_list = "\n".join([f"{i + 1}. {cert}" for i, cert in enumerate(csp_certifications[selected_csp])])
                await ctx.send(f"Select a certification for {selected_csp.upper()}:\n{cert_list}")
            else:
                await ctx.send("Invalid CSP selection. Please choose a valid cloud provider.")
        except ValueError:
            await ctx.send("Invalid input. Please enter the number corresponding to the CSP.")

    # Step 2: Handle certification selection
    elif step == "cert_selection":
        try:
            selection = int(selection)
            selected_csp = user_data[user_id]["csp"]
            if 1 <= selection <= len(csp_certifications[selected_csp]):
                selected_cert = csp_certifications[selected_csp][selection - 1]
                user_data[user_id]["cert"] = selected_cert
                user_data[user_id]["step"] = "exam_type_selection"

                # Present options for Standard or Custom exam
                await ctx.send(f"You've selected the certification {selected_cert}. Would you like to take a:\n"
                               "1. Standard Exam\n2. Custom Exam\n"
                               "Type the number corresponding to your choice.")
            else:
                await ctx.send("Invalid certification selection. Please choose a valid certification.")
        except ValueError:
            await ctx.send("Invalid input. Please enter the number corresponding to the certification.")

    # Step 3: Handle exam type selection (Standard or Custom)
    elif step == "exam_type_selection":
        if selection == "1":  # Standard exam
            user_data[user_id]["exam_type"] = "standard"
            user_data[user_id]["step"] = "question_selection"

            # Present a list of numbers for question count selection using numbers (1-24)
            question_options = "\n".join([f"{i}. {5 * i}" for i in range(1, 25)])  # Display 5, 10, ..., 120
            await ctx.send(f"How many questions would you like for the {user_data[user_id]['cert']} exam?\n"
                           f"Select from the following options:\n{question_options}")

        elif selection == "2":  # Custom exam
            user_data[user_id]["exam_type"] = "custom"
            user_data[user_id]["step"] = "topic_selection"

            # Ask the user to select the topics they want to cover
            selected_cert = user_data[user_id]["cert"]
            selected_csp = user_data[user_id]["csp"]
            if selected_cert in exam_topics[selected_csp]:
                topics = list(exam_topics[selected_csp][selected_cert].keys())  # Get the list of topic names
                topic_list = "\n".join([f"{i + 1}. {topic}" for i, topic in enumerate(topics)])
                await ctx.send(f"You've chosen a custom exam. Select the topics you'd like to cover for {selected_cert}:\n"
                               f"{topic_list}\n"
                               f"You can select multiple topics by typing their numbers separated by spaces like so: `stellar_select 1 3 5`.")
            else:
                await ctx.send(
                    f"Sorry, I couldn't find topics for the certification '{selected_cert}'. Please check the certification name.")
                return
        else:
            await ctx.send("Invalid selection. Please choose 1 for Standard or 2 for Custom.")

    # Step 4: Handle topic selection for custom exams
    elif step == "topic_selection":
        try:
            selected_csp = user_data[user_id]["csp"]
            selected_cert = user_data[user_id]["cert"]

            # Check if the selected certification exists in exam topics
            if selected_cert in exam_topics.get(selected_csp, {}):
                topics = list(exam_topics[selected_csp][selected_cert].keys())  # Get the list of topic names
            else:
                await ctx.send(
                    f"Sorry, I couldn't find topics for the certification '{selected_cert}'. Please check the certification name.")
                return

            # Parse the user's selected topics (expecting space-separated numbers)
            selected_topics = [int(t) for t in selection.split() if t.isdigit()]

            # Validate selected topics
            valid_topics = [i for i in selected_topics if 1 <= i <= len(topics)]

            if not valid_topics:
                await ctx.send("You didn't select any valid topics. Please choose topic numbers from the list.")
                return

            user_data[user_id]["custom_topics"] = [topics[i - 1] for i in valid_topics]  # Store selected topic names
            user_data[user_id]["step"] = "question_selection"

            # Present a list of numbers for question count selection
            question_options = "\n".join([f"{i}. {5 * i}" for i in range(1, 25)])  # Display 5, 10, ..., 120
            await ctx.send(
                f"Great! You've selected the following topics for your custom exam: {', '.join(user_data[user_id]['custom_topics'])}\n"
                f"How many questions would you like? Select from the following options:\n{question_options}")
        except ValueError:
            await ctx.send("Invalid input. Please select the topics by typing their numbers separated by spaces.")

    # Step 5: Handle number of questions for both standard and custom exams
    elif step == "question_selection":
        print("got here 1")
        # Trim any whitespace from the selection
        selection = selection.strip()
        print("got here 2")

        if not selection:  # Check for empty input
            print("got here 3")
            await ctx.send("You did not provide any input. Please enter a number for the question selection.")
            print("got here 4")
            return

        if selection.isdigit():
            print(selection)
            option_index = int(selection)

            # Ensure the user selected a valid option (1-24)
            if 1 <= option_index <= 24:  # Valid options are from 1 to 24
                num_questions = option_index * 5
                user_data[user_id]["num_questions"] = num_questions
                user_data[user_id]["step"] = "quiz_in_progress"

                # Check if the quiz is standard or custom
                is_custom = user_data[user_id]["exam_type"] == "custom"

                # Debugging output to check the values
                print(
                    f"User ID: {user_id}, Exam Type: {user_data[user_id]['exam_type']}, Num Questions: {num_questions}")

                # Generate quiz questions based on the selected certification or topics
                cert_or_topics = (
                    user_data[user_id]["cert"]
                    if not is_custom
                    else user_data[user_id]["custom_topics"]
                )

                # Ensure the correct certification/topics are being used
                if is_custom:
                    print(f"Custom Topics: {user_data[user_id]['custom_topics']}")
                else:
                    print(f"Selected Certification: {user_data[user_id]['cert']}")

                quiz_questions = await generate_quiz(cert_or_topics, num_questions, user_id, is_custom)

                # Ensure quiz_questions is not empty and is a list
                if quiz_questions and isinstance(quiz_questions, list):
                    active_quizzes[user_id] = quiz_questions

                    # Start asking the first question
                    await ctx.send(
                        f"Great! You've chosen {num_questions} questions.\nLet's start your quiz!\nHere is your first question:"
                    )
                    await ask_question(ctx, user_id)
                else:
                    await ctx.send("There was an error generating quiz questions. Please try again.")
                    print(f"Quiz Questions: {quiz_questions}")  # Debug output for generated questions
            else:
                await ctx.send("Please choose a valid option from the list (1-24).")
        else:
            await ctx.send("Please enter a valid number for the question selection.")


# Ask question function
async def ask_question(ctx, user_id):
    if user_id in active_quizzes and active_quizzes[user_id]:
        question_data = active_quizzes[user_id].pop(0)
        question = question_data["question"]
        choices = question_data["choices"]
        correct_answer = question_data["answer"]
        topic = question_data["topic"]

        # Save the question details for result tracking
        user_data[user_id]["current_question"] = {
            "question": question,
            "choices": choices,
            "correct_answer": correct_answer,
            "topic": topic  # Store the topic in the current question
        }

        await ctx.send(f"**Question:** {question}\n" +
                       "\n".join([f"{i + 1}. {choice}" for i, choice in enumerate(choices)]))
        await ctx.send("Please respond with the number of your answer choice.")
    else:
        await ctx.send("You've completed the quiz! 🎉")
        await show_results(ctx, user_id)  # Call function to display results after the quiz

# Handle answer submission
@bot.command(name="ans")
async def answer(ctx, selection: int):
    user_id = ctx.author.id
    if user_id not in user_data or "step" not in user_data[user_id] or user_data[user_id]["step"] != "quiz_in_progress":
        await ctx.send("You are not currently taking a quiz. Start one using `stellar_sq`.")
        return

    if user_id in active_quizzes:
        if 1 <= selection <= 4:
            # Get current question details
            current_question = user_data[user_id]["current_question"]
            question = current_question["question"]
            choices = current_question["choices"]
            correct_answer = current_question["correct_answer"]
            topic = current_question["topic"]  # Get the question's topic

            selected_answer = choices[selection - 1].strip()  # User's selected answer
            is_correct = selected_answer in correct_answer

            # Save the answer result
            if "results" not in user_data[user_id]:
                user_data[user_id]["results"] = []

            user_data[user_id]["results"].append({
                "question": question,
                "choices": choices,
                "selected_answer": selected_answer,  # Store the selected answer text
                "correct_answer": correct_answer,    # Store the correct answer text
                "is_correct": is_correct,
                "topic": topic  # Include the topic in the result
            })
            print(f"selected: {selected_answer}")
            print(f"{correct_answer}")
            print(f"comparison: {selected_answer == correct_answer}")
            show_invisible_characters(selected_answer)
            print()
            show_invisible_characters(correct_answer)
            # Provide feedback
            if is_correct:
                await ctx.send("Correct! ✅")
            else:
                await ctx.send(f"Incorrect. ❌ The correct answer was: {correct_answer}")

            # Ask the next question or show results if completed
            await ask_question(ctx, user_id)
        else:
            await ctx.send("Invalid choice. Please select a number between 1 and 4.")
    else:
        await ctx.send("No active quiz found. Please start a quiz.")


# Function to display results after the quiz is completed
async def show_results(ctx, user_id):
    # Ensure user has results stored in their data
    if user_id in user_data and "results" in user_data[user_id]:
        results = user_data[user_id]["results"]
        correct_answers = sum(1 for result in results if result["is_correct"])
        total_questions = len(results)
        score_percentage = (correct_answers / total_questions) * 100

        # Calculate correct answers per topic
        topic_correct_counts = {}
        for result in results:
            topic = result["topic"]
            if topic not in topic_correct_counts:
                topic_correct_counts[topic] = {"correct": 0, "total": 0}

            topic_correct_counts[topic]["total"] += 1
            if result["is_correct"]:
                topic_correct_counts[topic]["correct"] += 1

        # Create a detailed breakdown of the user's answers
        summary = []
        summary.append(f"Quiz complete! 🎉 You scored {correct_answers}/{total_questions} ({score_percentage:.2f}%)\n")
        summary.append("Here's a breakdown of your answers:\n")

        for i, result in enumerate(results, 1):
            summary.append(
                f"**Q{i}:** {result['question']}\n"
                f"Your answer: {result['selected_answer']}\n"
                f"Correct answer: {result['correct_answer']}\n"
                f"{'✅ Correct' if result['is_correct'] else '❌ Incorrect'}\n\n"
            )

        # Add per-topic performance
        summary.append("\n**Performance by Topic:**\n")
        for topic, count in topic_correct_counts.items():
            topic_score = (count["correct"] / count["total"]) * 100
            summary.append(f"{topic}: {count['correct']}/{count['total']} correct ({topic_score:.2f}%)\n")

        # Convert summary list to string
        result_text = "\n".join(summary)

        # Create a temporary file with the result using utf-8 encoding
        file_name = f"{ctx.author.name}_quiz_results.txt"
        with open(file_name, "w", encoding="utf-8") as result_file:
            result_file.write(result_text)

        # Send the file in Discord
        await ctx.send(file=discord.File(file_name))

        # Delete the file from local storage after sending
        os.remove(file_name)

        # Prepare results for JSON storage
        data = load_json()
        if str(user_id) not in data:
            data[str(user_id)] = {}

        data[str(user_id)]["results"] = {
            "score": score_percentage,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "details": results
        }
        save_json(data)

        # After posting the results, proceed to clean up the JSON file
        # Check if the user exists in the data, then delete the user's data
        if str(user_id) in data:
            del data[str(user_id)]

        # Save the updated JSON file without the user's data
        save_json(data)

        # Clear the user's data from user_data to free up memory
        del user_data[user_id]
    else:
        await ctx.send("No results found for this quiz.")
# Run the bot
bot.run(BOT_TOKEN)  # Replace with your Discord bot token