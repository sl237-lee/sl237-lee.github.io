
variable "region" { type = string  default = "us-east-1" }
variable "name"   { type = string  default = "claims-pl" }
variable "vpc_cidr" { type = string default = "10.20.0.0/16" }
variable "azs" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}
variable "private_subnets" {
  type    = list(string)
  default = ["10.20.1.0/24", "10.20.2.0/24"]
}
variable "allowed_cidrs" {
  type    = list(string)
  default = ["10.0.0.0/8"]
}
