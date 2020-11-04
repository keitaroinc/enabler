/*
Copyright © 2020 Keitaro Inc dev@keitaro.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
package preflight

import (
	"github.com/keitaroinc/enabler/cmd/colors"
	"github.com/keitaroinc/enabler/cmd/util"
	"github.com/spf13/cobra"
	"os"
	"os/exec"
	"strconv"
	"strings"
)

// TODO: Specify versions and dependencies via config file?

// preflightCmd represents the preflight command
var MainCmd = &cobra.Command{
	Use:   "preflight",
	Short: "Checks if required dependencies are installed in the system",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: func(cmd *cobra.Command, args []string) {
		log := util.NewLogger("INFO", nil)
		// check if java is present on the system
		command := exec.Command("java", "--version")
		cmdOut, err := command.Output()
		if err != nil {
			// java is not present in the system
			log.Info(string(colors.RED), "java is not present on the machine, terminating...")
			os.Exit(126)
		}
		version := strings.Split(string(cmdOut), " ")
		if strings.HasPrefix(version[1], "11") {
			log.Info(string(colors.WHITE), "java jdk 11", util.Okay())
		} else {
			log.Fatal(string(colors.RED), "Java JDK 11 needed, please change the version of java on your machine.")
		}

		// figure out if there's a better way to check for required dependencies???

		// check if docker is present on the system
		command = exec.Command("docker", "version", "-f", "{{.Server.Version}}")
		cmdOut, err = command.Output()
		if err != nil {
			// docker is not present in the system
			log.Fatal(string(colors.RED), "docker is not present on the machine, terminating...")
		} else {
			log.Info(string(colors.WHITE), "docker "+strings.TrimSpace(string(cmdOut)), util.Okay())
		}
		// check if helm is present on the system
		command = exec.Command("helm", "version", "--short")
		cmdOut, err = command.Output()
		if err != nil {
			// helm is not present in the system
			log.Fatal(string(colors.RED), "helm is not present on the machine, terminating...")
		}
		if strings.HasPrefix(strings.TrimSpace(string(cmdOut)), "v3") {
			log.Info(string(colors.WHITE), "helm "+strings.TrimSpace(string(cmdOut)), util.Okay())
		} else {
			log.Fatal(string(colors.RED), "helm 3 needed, please install it on the machine.")
		}
		// check if kind is present on the system
		command = exec.Command("kind", "version")
		cmdOut, err = command.Output()
		if err != nil {
			// kind is not present in the system
			log.Fatal(string(colors.RED), "kind is not present on the machine, terminating...")
		} else {
			log.Info(string(colors.WHITE), strings.TrimSpace(string(cmdOut)), util.Okay())
		}
		// check if skaffold is present on the system
		command = exec.Command("skaffold", "version")
		cmdOut, err = command.Output()
		if err != nil {
			// skaffold is not present in the system
			log.Fatal(string(colors.RED), "skaffold is not present on the machine, terminating...")
		} else {
			log.Info(string(colors.WHITE), "skaffold "+strings.TrimSpace(string(cmdOut)), util.Okay())
		}
		// check if kubectl is present on the system
		command = exec.Command("kubectl", "version", "--client=true", "--short=true")
		cmdOut, err = command.Output()
		if err != nil {
			// kubectl is not present in the system
			log.Fatal(string(colors.RED), "kubectl is not present on the machine, terminating...")
		} else {
			log.Info(string(colors.WHITE), "kubectl "+strings.TrimSpace(strings.ToLower(string(cmdOut))), util.Okay())
		}
		// check if istioctl is present on the system
		command = exec.Command("istioctl", "version", "-s", "--remote=false")
		cmdOut, err = command.Output()
		if err != nil {
			// istio is not present in the system
			log.Fatal(string(colors.RED), "istioctl is not present on the machine, terminating...")
		}
		version = strings.Split(strings.TrimSpace(string(cmdOut)), ".")
		minorVer, err := strconv.Atoi(version[1])
		if err != nil {
			log.Fatal(string(colors.RED), "unable to parse istio version, terminating...")
		}
		if minorVer >= 5 {
			log.Info(string(colors.WHITE), "istio "+strings.TrimSpace(string(cmdOut)), util.Okay())
		} else {
			log.Fatal(string(colors.RED), "istio 1.5 or greater needed, please update the version of istio on your machine.")
		}
	},
}

func init() {
	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// MainCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// MainCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")

	// initialize and register sub-commands e.g.:
	// MainCmd.AddCommand(sub)
}
