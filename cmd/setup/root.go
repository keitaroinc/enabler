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
package setup

import (
	"fmt"
	"github.com/keitaroinc/enabler/cmd/util"
	"github.com/spf13/cobra"
	"io"
	"net/http"
	"os"
)

// setupCmd represents the setup command
var MainCmd = &cobra.Command{
	Use:   "setup",
	Short: "Setup infrastructure services",
	Long: `You can use the setup command to download and configure all infrastructure services such as: kind, kubectl, istioctl, helm and skaffold`,
	Run: func(cmd *cobra.Command, args []string) {


		// print help
		_ = cmd.Help()
	},
}

func init() {
	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// MainCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:

	// MainCmd.Flags().BoolVarP(&initFlag, "init", "i", false, "Download and configure all services")

	// initialize and register sub-commands e.g.:
	// MainCmd.AddCommand(sub)
	MainCmd.AddCommand(initCmd)
	MainCmd.AddCommand(istioCmd)
	MainCmd.AddCommand(metallbCmd)
}

func InstallDependency(name string, url string, dest string) error {
	log := util.NewLogger("INFO", nil)
	err := Download(dest, url)
	if err != nil {
		fmt.Println("SOME ERROR")
		return err
	} else {
		log.Infof("%s download complete.", name)
	}
	err = os.Chmod(dest, 0755)
	if err != nil {
		log.Fatal(err)
		return err
	}
	log.Infof("%s installed successfully.", name)
	return nil
}

func Download(path string, url string) error {
	log := util.NewLogger("INFO", nil)
	log.Infof("Downloading %s ...", url)
	// Get the data
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// Create the file
	out, err := os.Create(path)
	if err != nil {
		return err
	}
	defer out.Close()

	// Write the body to file
	_, err = io.Copy(out, resp.Body)
	return err
}