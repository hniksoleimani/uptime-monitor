# ===========================================================
# EKS Cluster
# ===========================================================
# This is the Kubernetes control plane — managed by AWS.
# You don't pay for the control plane separately (it's included).
# You only pay for the worker nodes (EC2 instances).

resource "aws_eks_cluster" "main" {
  name     = "${var.project_name}-eks"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.31" # latest stable K8s version on EKS
  access_config {
    authentication_mode = "API_AND_CONFIG_MAP"
  }
  vpc_config {
    subnet_ids = concat(
      aws_subnet.public[*].id,
      aws_subnet.private[*].id,
    )
    endpoint_public_access  = true # you can run kubectl from your laptop
    endpoint_private_access = true # nodes can reach the API server internally
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
  ]

  tags = { Name = "${var.project_name}-eks" }
}

# ===========================================================
# EKS Managed Node Group
# ===========================================================
# These are the actual EC2 instances that run your pods.
# "Managed" means AWS handles node provisioning, updates,
# and draining — you just specify instance type and count.

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.project_name}-nodes"
  node_role_arn   = aws_iam_role.eks_nodes.arn

  # Nodes go in private subnets (not internet-facing)
  subnet_ids = aws_subnet.private[*].id

  instance_types = [var.eks_node_instance_type]

  scaling_config {
    desired_size = var.eks_desired_nodes
    min_size     = 1
    max_size     = 4
  }

  # Optional: force update if a new AMI is available
  update_config {
    max_unavailable = 1 # roll one node at a time during updates
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ecr_read_only,
  ]

  tags = { Name = "${var.project_name}-nodes" }
}
