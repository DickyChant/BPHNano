#!/bin/bash
# Check status or resubmit all submitted CRAB jobs
# Usage:
#   ./check_crab_status.sh [status|resubmit|kill] [options]
#   ./check_crab_status.sh status          # Check status (default)
#   ./check_crab_status.sh resubmit        # Resubmit failed jobs
#   ./check_crab_status.sh resubmit --force # Force resubmit all jobs
#   ./check_crab_status.sh kill            # Kill all jobs
#   ./check_crab_status.sh resubmit --improve_resubmit # Resubmit with increased walltime, memory, and T2_CH_CERN site

# Default command is 'status'
CRAB_CMD="${1:-status}"
shift  # Remove first argument, keep remaining options

# Check for --improve_resubmit flag
IMPROVE_RESUBMIT=false
REMAINING_ARGS=()
for arg in "$@"; do
    if [[ "$arg" == "--improve_resubmit" ]]; then
        IMPROVE_RESUBMIT=true
    else
        REMAINING_ARGS+=("$arg")
    fi
done

# Create timestamped folder for verbose error logs
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_DIR="crab_status_logs/${TIMESTAMP}"

# Validate command
if [[ ! "$CRAB_CMD" =~ ^(status|resubmit|kill|report|getoutput)$ ]]; then
    echo "Error: Invalid CRAB command '$CRAB_CMD'"
    echo "Valid commands: status, resubmit, kill, report, getoutput"
    exit 1
fi

# Set appropriate message based on command
case "$CRAB_CMD" in
    status)
        echo "Checking status of all CRAB jobs..."
        ;;
    resubmit)
        echo "Resubmitting failed CRAB jobs..."
        if [[ "${REMAINING_ARGS[@]}" == *"--force"* ]]; then
            echo "WARNING: --force flag detected. This will resubmit ALL jobs, not just failed ones."
        fi
        if [ "$IMPROVE_RESUBMIT" = true ]; then
            echo "INFO: --improve_resubmit flag detected. Will increase walltime, memory, and whitelist T2_CH_CERN."
        fi
        ;;
    kill)
        echo "Killing all CRAB jobs..."
        echo "WARNING: This will kill all running jobs!"
        ;;
    report)
        echo "Generating reports for all CRAB jobs..."
        ;;
    getoutput)
        echo "Getting output for all CRAB jobs..."
        ;;
esac

echo "======================================"
echo ""

# Find all directories that match the CRAB task pattern (crab_*)
# These are typically 2 levels deep: workarea/crab_taskname/
find . -type d -name "crab_*" | sort | while read -r dir; do
    echo ""
    echo "======================================"
    echo "Processing: $dir"
    echo "Command: $CRAB_CMD"
    echo "======================================"
    
    # Execute the appropriate CRAB command
    case "$CRAB_CMD" in
        status)
            # Capture output to check for failures
            STATUS_OUTPUT=$(crab status -d "$dir" 2>&1)
            echo "$STATUS_OUTPUT"
            
            # Check for actual failures (not just warnings)
            HAS_FAILURES=false
            
            # Check scheduler status for FAILED
            if echo "$STATUS_OUTPUT" | grep -qi "Status on the scheduler:.*FAILED"; then
                HAS_FAILURES=true
            fi
            
            # Check jobs status line for "failed" keyword (but not "finished")
            # Pattern: "failed" with a percentage that's not 0.0%
            if echo "$STATUS_OUTPUT" | grep -qiE "Jobs status:.*failed.*[1-9]"; then
                HAS_FAILURES=true
            fi
            
            # Check for Error Summary section (indicates failures)
            if echo "$STATUS_OUTPUT" | grep -qi "Error Summary:"; then
                # Only flag as failure if there are actual error counts
                if echo "$STATUS_OUTPUT" | grep -qiE "jobs failed with exit code"; then
                    HAS_FAILURES=true
                fi
            fi
            
            # Only show failure warning if we detected actual failures
            if [ "$HAS_FAILURES" = true ]; then
                echo ""
                echo "⚠️  This job has failures!"
                
                # Get verbose errors and save to timestamped log folder
                echo "Collecting verbose error information..."
                mkdir -p "$LOG_DIR"
                
                # Extract task name from directory path (e.g., crab_taskname)
                TASK_NAME=$(basename "$dir")
                VERBOSE_LOG="${LOG_DIR}/${TASK_NAME}_verboseErrors.log"
                
                # Capture verbose errors
                crab status --verboseErrors -d "$dir" > "$VERBOSE_LOG" 2>&1
                echo "Verbose errors saved to: $VERBOSE_LOG"
            fi
            ;;
        resubmit)
            if [ "$IMPROVE_RESUBMIT" = true ]; then
                # Resubmit with improved settings:
                # - Increase walltime to 2750 minutes (~46 hours, close to max)
                # - Increase memory to 5000 MB (maximum allowed for 1-core jobs)
                # - Whitelist T2_CH_CERN site
                echo "Resubmitting with improved settings: maxjobruntime=2750, maxmemory=5000, sitewhitelist=T2_CH_CERN"
                crab resubmit -d "$dir" --maxjobruntime=2750 --maxmemory=5000 --sitewhitelist=T2_CH_CERN "${REMAINING_ARGS[@]}"
            else
                crab resubmit -d "$dir" "${REMAINING_ARGS[@]}"
            fi
            ;;
        kill)
            crab kill -d "$dir" "${REMAINING_ARGS[@]}"
            ;;
        report)
            crab report -d "$dir" "${REMAINING_ARGS[@]}"
            ;;
        getoutput)
            crab getoutput -d "$dir" "${REMAINING_ARGS[@]}"
            ;;
    esac
    
    echo ""
done

echo ""
echo "======================================"
echo "Finished processing all CRAB jobs"
echo "======================================"

# Show log directory if it was created
if [ -d "$LOG_DIR" ]; then
    echo ""
    echo "Verbose error logs saved to: $LOG_DIR"
    echo "Files in log directory:"
    ls -lh "$LOG_DIR"
fi
