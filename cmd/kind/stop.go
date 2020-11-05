package kind

import (
	"context"
	"fmt"
	"github.com/briandowns/spinner"
	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/filters"
	"github.com/docker/docker/client"
	"github.com/keitaroinc/enabler/cmd/util"
	"github.com/spf13/cobra"
	"os"
	"os/exec"
	"time"
)

var stopCmd = &cobra.Command{
	Use:   "stop",
	Short: "Stop kind cluster",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		log := util.NewLogger("INFO", nil)
		// Kind creates containers with a label io.x-k8s.kind.cluster
		// Kind naming is clustername-control-plane and clustername-worker{x}
		// The idea is to find the containers and stop them
		kubeContext := cmd.Flag("kube-context").Value
		err := getKind(kubeContext.String())
		if err != nil {
			log.Errorf("Kind cluster %s doesn't exist, terminating.", kubeContext)
			if err, ok := err.(*exec.ExitError); ok {
				os.Exit(err.ExitCode())
			}
		} else {
			// init docker client
			cli, err := client.NewEnvClient()
			if err != nil {
				panic(err)
			}
			// create filter and get relevant containers
			// TODO: improve filters
			f := filters.NewArgs()
			f.Add("name", fmt.Sprintf("%s-control-plane", kubeContext))
			f.Add("name", fmt.Sprintf("%s-worker", kubeContext))
			// f.Add("label", "io.x-k8s.kind.cluster")

			containers, err := cli.ContainerList(context.Background(), types.ContainerListOptions{Filters: f, All: true})
			if err != nil {
				// network not found
				panic(err)
			}
			// stop the running containers
			s := spinner.New(spinner.CharSets[9], 100*time.Millisecond)
			s.Color("green")
			s.Prefix = "Stopping containers "
			s.Start()
			stopDuration := 5000*time.Millisecond
			for _, container := range containers {
				switch container.State {
				case "running":
					err := cli.ContainerStop(context.Background(), container.ID, &stopDuration)
					if err != nil {
						log.Errorf("Unable to stop container: %s", container.Names[0])
					} else {
						log.Infof("Container %s stopped.", container.Names[0])
					}
				default:
					log.Infof("Cannot stop container %s because it is in %s status.", container.Names[0], container.State)
				}
			}
			// sleep 1 sec before stopping the spinner
			time.Sleep(1 * time.Second)
			s.Stop()
			log.Infof("Kind cluster \"%s\" was stopped.", kubeContext)
		}
	},
}

