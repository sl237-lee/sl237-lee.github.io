
output "vpc_id" {
  value = module.vpc.vpc_id
}
output "endpoint_id" {
  value = aws_vpc_endpoint.snowflake.id
}
