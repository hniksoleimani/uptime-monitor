# ===========================================================
# ECR Repository
# ===========================================================
# This is where your Docker images live in AWS.
# EKS nodes pull images from here (that's why they need
# the AmazonEC2ContainerRegistryReadOnly IAM policy).

resource "aws_ecr_repository" "app" {
  name                 = var.project_name
  image_tag_mutability = "MUTABLE" # allows overwriting tags (e.g., "latest")
  force_delete         = true      # allows deleting repo even with images in it

  image_scanning_configuration {
    scan_on_push = true # automatically scan images for vulnerabilities
  }

  tags = { Name = "${var.project_name}-ecr" }
}

# Clean up old images to save storage costs
resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = {
        type = "expire"
      }
    }]
  })
}
