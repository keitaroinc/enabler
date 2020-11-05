package setup

import (
	"context"
	"encoding/binary"
	"fmt"
	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/filters"
	"github.com/docker/docker/client"
	"github.com/keitaroinc/enabler/cmd/util"
	"github.com/spf13/cobra"
	"net"
	"os"
	"os/exec"
	"strings"
)

var metallbCmd = &cobra.Command{
	Use:   "metallb",
	Short: "Configure metallb",
	Long:  `Verify system installation of metallb and check if we are ready to setup metallb`,
	Run: func(cmd *cobra.Command, args []string) {
		log := util.NewLogger("INFO", nil)
		kubeContext := cmd.Flag("kube-context").Value
		// check if metallb is present on the system
		command := exec.Command("helm", "status", "metallb",
			"-n", "metallb",
			"--kube-context", fmt.Sprintf("kind-%s", kubeContext),
		)
		_, err := command.Output()
		if err != nil {
			// metallb is not present in the system
			log.Fatal("Metallb not found...installing.")
		}
		log.Infof("Installing metallb, please wait...")

		// get docker client
		cli, err := client.NewEnvClient()
		if err != nil {
			panic(err)
		}

		// create filter to get bridge network
		f := filters.NewArgs()
		f.Add("name", "bridge")

		dockerBridge, err := cli.NetworkList(context.Background(), types.NetworkListOptions{Filters: f})
		if err != nil {
			// network not found
			panic(err)
		}

		bridgeSubnet := dockerBridge[0].IPAM.Config[0].Subnet
		log.Infof("Using docker bridge subnet: %s", bridgeSubnet)
		_, networkIPs, err := net.ParseCIDR(bridgeSubnet)
		if err != nil {
			log.Fatal(err)
		}
		// convert IPNet struct mask and address to uint32
		mask := binary.BigEndian.Uint32(networkIPs.Mask)
		start := binary.BigEndian.Uint32(networkIPs.IP)

		// extract last 10 addresses to be used for metallb
		// loop through addresses as uint32
		var metallbIPs []net.IP
		finish := (start & mask) | (mask ^ 0xffffffff)
		for i := start + (finish - start - 9); i <= finish; i++ {
			// convert back to net.IP
			ip := make(net.IP, 4)
			binary.BigEndian.PutUint32(ip, i)
			metallbIPs = append(metallbIPs, ip)
		}

		// Metallb layer2 configuration
		// TODO: extract config as template?
		var metallbConfig = []string{"configInline.address-pools[0].name=default,",
			"configInline.address-pools[0].protocol=layer2,",
			fmt.Sprintf("configInline.address-pools[0].addresses[0]=%s-%s",
				metallbIPs[0].String(),
				metallbIPs[len(metallbIPs)-1].String()),
		}

		// create metallb namespace
		command = exec.Command("kubectl", "get", "ns", "metallb",
			"--context", fmt.Sprintf("kind-%s", kubeContext),
		)
		cmdOut, err := command.Output()
		if err != nil {
			// try to create the metallb namespace
			command = exec.Command("kubectl", "create", "ns", "metallb",
				"--context", fmt.Sprintf("kind-%s", kubeContext),
			)
			if err, ok := err.(*exec.ExitError); ok {
				log.Fatal("Could not create namespace for metallb, terminating.")
				os.Exit(err.ExitCode())
			}
		} else {
			log.Infof("metallb namespace %s already exists, skipping creation.", cmdOut)
		}

		// install metallb on the cluster
		command = exec.Command("helm", "install",
			"--kube-context", fmt.Sprintf("kind-%s", kubeContext),
			"metallb",
			"--set", strings.Join(metallbConfig, ""),
			"-n", "metallb", "stable/metallb",
		)
		_, err = command.Output()
		if err != nil {
			log.Error(err)
			log.Fatal("Could not install metallb, terminating.")
		} else {
			log.Info("Metallb installed on the cluster.")
		}
	},
}
