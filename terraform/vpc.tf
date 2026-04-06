# ===========================================================
# VPC
# ===========================================================
# Think of a VPC as your own private data center inside AWS.
# Nothing can talk to anything outside unless you explicitly allow it.

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true # needed for EKS and RDS DNS resolution
  enable_dns_support   = true

  tags = { Name = "${var.project_name}-vpc" }
}

# ===========================================================
# Subnets
# ===========================================================
# Public subnets: for the ALB (load balancer) — internet-facing
# Private subnets: for EKS nodes and RDS — no direct internet access
#
# We create 2 of each in different AZs for high availability.
# If one AZ goes down, the other keeps running.

resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index) # 10.0.0.0/24, 10.0.1.0/24
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true # instances here get public IPs

  tags = {
    Name                                           = "${var.project_name}-public-${count.index + 1}"
    "kubernetes.io/role/elb"                        = "1" # tells EKS this subnet is for public load balancers
    "kubernetes.io/cluster/${var.project_name}-eks" = "shared"
  }
}

resource "aws_subnet" "private" {
  count = 2

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10) # 10.0.10.0/24, 10.0.11.0/24
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name                                           = "${var.project_name}-private-${count.index + 1}"
    "kubernetes.io/role/internal-elb"               = "1" # for internal load balancers
    "kubernetes.io/cluster/${var.project_name}-eks" = "shared"
  }
}

# ===========================================================
# Internet Gateway
# ===========================================================
# The door between your VPC and the internet.
# Without this, nothing in your VPC can reach the outside world.

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = { Name = "${var.project_name}-igw" }
}

# ===========================================================
# NAT Gateway
# ===========================================================
# Private subnets can't access the internet directly (by design).
# But your EKS nodes need to pull Docker images from ECR.
# NAT Gateway lets private resources make OUTBOUND requests
# without being reachable from the internet (one-way door).

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = { Name = "${var.project_name}-nat-eip" }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id # NAT GW lives in a public subnet

  tags = { Name = "${var.project_name}-nat" }

  depends_on = [aws_internet_gateway.main]
}

# ===========================================================
# Route Tables
# ===========================================================
# Route tables = traffic rules. "If you want to go to X, go through Y."

# Public route table: send internet traffic through the Internet Gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0" # all internet traffic
    gateway_id = aws_internet_gateway.main.id
  }

  tags = { Name = "${var.project_name}-public-rt" }
}

# Associate public subnets with public route table
resource "aws_route_table_association" "public" {
  count = 2

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private route table: send internet traffic through the NAT Gateway
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = { Name = "${var.project_name}-private-rt" }
}

# Associate private subnets with private route table
resource "aws_route_table_association" "private" {
  count = 2

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}
