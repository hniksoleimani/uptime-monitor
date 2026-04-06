# Get available AZs in the region automatically
# Instead of hardcoding "eu-central-1a", "eu-central-1b",
# this works if you change the region later.
data "aws_availability_zones" "available" {
  state = "available"
}
