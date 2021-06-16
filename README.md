# Pexip Transcoder Client
A simple CLI library for manually configuring Pexip Transcoder Nodes in a cloud. The specific
use-case that this is intended for is in spinning up Pexip Transcoder nodes in AWS using Terraform 
outputs the inputs to the code.

Are there better ways to do this? Yes, [probably](https://docs.pexip.com/admin/smart_scale.htm). But this way also does work, and it was an opportunity
for me to mimic the layout of a piece of Python code that inspired me to work on this in the first place,
[httpie](https://github.com/httpie/httpie)

## Workflow

