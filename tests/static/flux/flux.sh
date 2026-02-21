#!/bin/bash
# flux: --job-name={{job_name}}
# flux: --env=CORES={{cores}}
# flux: --output=time.out
# flux: --error=error.out
# flux: -n {{cores}}
{%- if run_time_max %}
# flux: -t {{run_time_max}}
{%- endif %}
{%- if dependency_list %}
{%- for jobid in dependency_list %}
# flux: --dependency=afterok:{{jobid}}
{%- endfor %}
{%- endif %}

{{command}}