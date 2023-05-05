#!/bin/bash
#flux: -n{{cores}} --job-name={{job_name}} --env=CORES={{cores}} --output=time.out --error=error.out
{{command}}