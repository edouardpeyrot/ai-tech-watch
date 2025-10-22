terraform {
  source = "../../terraform-modules/aws/cluster"
}

include "root" {
  path = find_in_parent_folders("root.hcl")
}

