# ===========================================================
# RDS Security Group
# ===========================================================
# Only allow PostgreSQL traffic (port 5432) from EKS nodes.
# The database should NEVER be reachable from the internet.

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Allow PostgreSQL from EKS nodes only"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-rds-sg" }
}

# ===========================================================
# EKS Nodes Security Group
# ===========================================================
# EKS creates its own security groups, but we define one
# so we can reference it in the RDS rules above.

resource "aws_security_group" "eks_nodes" {
  name        = "${var.project_name}-eks-nodes-sg"
  description = "Security group for EKS worker nodes"
  vpc_id      = aws_vpc.main.id

  # Allow all outbound (nodes need to pull images, talk to AWS APIs, etc.)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-eks-nodes-sg" }
}


data "aws_security_group" "eks_cluster_auto" {
  filter {
    name   = "group-name"
    values = ["eks-cluster-sg-${var.project_name}-eks-*"]
  }
  depends_on = [aws_eks_cluster.main]
}

resource "aws_security_group_rule" "rds_from_eks_cluster_sg" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds.id
  source_security_group_id = data.aws_security_group.eks_cluster_auto.id
  description              = "Allow EKS managed node group (uses cluster auto-SG) to reach RDS"
}
