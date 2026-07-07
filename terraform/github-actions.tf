# ===========================================================
# GitHub Actions OIDC Provider
# ===========================================================
# Instead of storing long-lived AWS access keys in GitHub Secrets,
# GitHub Actions authenticates to AWS via OIDC (short-lived tokens).
# GitHub signs a JWT identifying the workflow; AWS trusts GitHub's
# signature via this provider, then issues temporary STS credentials.
# Zero secrets to store or rotate.

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
  ]
  tags = { Name = "${var.project_name}-github-oidc" }
}

# ===========================================================
# IAM Role for GitHub Actions
# ===========================================================
# The trust policy restricts which GitHub workflow can assume this role.
# The "sub" claim in the GitHub token looks like:
#   repo:hniksoleimani/uptime-monitor:ref:refs/heads/main
# StringLike "repo:hniksoleimani/uptime-monitor:*" allows all branches.
# Tighter option: pin to main only. For a portfolio project, * is fine.

resource "aws_iam_role" "github_actions" {
  name = "${var.project_name}-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.github.arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:hniksoleimani/uptime-monitor:*"
        }
      }
    }]
  })
  tags = { Name = "${var.project_name}-github-actions-role" }
}

# ===========================================================
# ECR push permissions
# ===========================================================
# Two-part: GetAuthorizationToken must be Resource="*" (AWS limit).
# All other actions scoped to OUR repository ARN only.

resource "aws_iam_policy" "github_actions_ecr" {
  name        = "${var.project_name}-github-actions-ecr"
  description = "Allow GitHub Actions to push Docker images to ECR"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = aws_ecr_repository.app.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_actions_ecr" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_actions_ecr.arn
}

# ===========================================================
# EKS DescribeCluster (needed for `aws eks update-kubeconfig`)
# ===========================================================
# Inline policy — no need for a standalone reusable policy.

resource "aws_iam_role_policy" "github_actions_eks_describe" {
  name = "${var.project_name}-github-actions-eks-describe"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "eks:DescribeCluster"
      Resource = aws_eks_cluster.main.arn
    }]
  })
}

# ===========================================================
# EKS Access Entry
# ===========================================================
# IAM permission to describe the cluster != permission to run kubectl.
# Access entries map the IAM role to Kubernetes permissions inside the
# cluster. This is the modern replacement for the aws-auth configmap.

resource "aws_eks_access_entry" "github_actions" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.github_actions.arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "github_actions_admin" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.github_actions.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  access_scope {
    type = "cluster"
  }
}

# ===========================================================
# Terraform User Access Entry
# ===========================================================
# In API_AND_CONFIG_MAP auth mode, the cluster creator does NOT
# get auto-admin. The IAM user running terraform apply must be
# explicitly granted access. Otherwise kubectl fails with 401.

resource "aws_eks_access_entry" "terraform_user" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = "arn:aws:iam::456493253522:user/terraform"
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "terraform_user_admin" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = "arn:aws:iam::456493253522:user/terraform"
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  access_scope {
    type = "cluster"
  }
}
