package kind

import (
	"github.com/keitaroinc/enabler/cmd/util"
	"github.com/spf13/cobra"
	"os"
	"os/exec"
)

var config string

var createCmd = &cobra.Command{
	Use:   "create",
	Short: "Create a kind cluster",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		log := util.NewLogger("INFO", nil)
		if config != ""{
			// check if the kind cluster already exists
			kubeContext := cmd.Flag("kube-context").Value
			err := getKind(kubeContext.String())
			if err != nil {
				log.Infof("Kind cluster %s doesn't exist, continue with creation.", kubeContext)
			} else {
				log.Infof("Kind cluster %s already exists, skipping creation.", kubeContext)
				os.Exit(0)
			}

			// create the kind cluster
			command := exec.Command("kind", "create", "cluster",
				"--name", kubeContext.String(),
				"--config", config,
			)
			_, err = command.Output()
			if err != nil {
				// unable to create the cluster
				log.Errorf("Unable to create the cluster: %s", kubeContext)
				if err, ok := err.(*exec.ExitError); ok {
					os.Exit(err.ExitCode())
				}
			}
			log.Infof("Kind cluster %s created.", kubeContext)
		} else {
			cmd.Help()
		}
	},
}

func init() {
	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// namesoaceCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	createCmd.Flags().StringVarP(&config, "config-file", "", "kind-cluster.yaml", "cluster config path")
}