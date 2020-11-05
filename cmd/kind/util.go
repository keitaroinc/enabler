package kind

import (
	"fmt"
	"github.com/docker/docker/api/types"
	"github.com/keitaroinc/enabler/cmd/util"
	"github.com/pkg/errors"
	"os/exec"
	"strings"
)

func getKind(cluster string) error {
	log := util.NewLogger("INFO", nil)
	command := exec.Command("kind", "get", "clusters")
	cmdOut, err := command.Output()
	if err != nil {
		// unable to get kind clusters
		log.Errorf("Unable to get kind cluster: %s", cluster)
		if err, ok := err.(*exec.ExitError); ok {
			log.Error(err.ExitCode())
			return err
		}
	}
	clusters := strings.Split(string(cmdOut), "\n")
	_, found := util.InSlice(clusters, cluster)
	if found {
		return nil
	}
	return errors.New(fmt.Sprintf("Cluster %s not found.", cluster))
}

func getClusterInfo(cluster string) error {
	command := exec.Command("kubectl", "cluster-info", "--context", fmt.Sprintf("kind-%s", cluster))
	_, err := command.Output()
	if err != nil {
		return err
	}
	return nil
}

func setKubeConfig(container types.Container, cluster string) error {
	log := util.NewLogger("INFO", nil)
	command := exec.Command("kubectl", "config", "set-cluster", fmt.Sprintf("kind-%s", cluster),
		"--server", fmt.Sprintf("https://127.0.0.1:%d", container.Ports[0].PublicPort))
	_, err := command.Output()
	if err != nil {
		// unable to set kube config
		log.Errorf("Unable to set kube config: %s", cluster)
		return err
	}
	return nil
}