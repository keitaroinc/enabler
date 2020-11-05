package kind

import (
	"github.com/keitaroinc/enabler/cmd/util"
	"github.com/spf13/cobra"
	"os"
	"os/exec"
)

var deleteCmd = &cobra.Command{
	Use:   "delete",
	Short: "Delete kind cluster",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		log := util.NewLogger("INFO", nil)
		// check if the kind cluster exists
		kubeContext := cmd.Flag("kube-context").Value
		err := getKind(kubeContext.String())
		if err != nil {
			log.Errorf("Kind cluster %s doesn't exist, terminating.", kubeContext)
			if err, ok := err.(*exec.ExitError); ok {
				os.Exit(err.ExitCode())
			}
		}
		// delete the cluster
		command := exec.Command("kind", "delete", "cluster", "--name", kubeContext.String())
		_, err = command.Output()
		if err != nil {
			// unable to delete the cluster
			log.Errorf("Unable to delete kind cluster: %s", kubeContext)
			if err, ok := err.(*exec.ExitError); ok {
				os.Exit(err.ExitCode())
			}
		}
		log.Infof("Kind cluster %s deleted.", kubeContext)
	},
}
