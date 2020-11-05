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
package cmd

import (
	"fmt"
	"github.com/keitaroinc/enabler/cmd/apps"
	"github.com/keitaroinc/enabler/cmd/kind"
	"github.com/keitaroinc/enabler/cmd/platform"
	"github.com/keitaroinc/enabler/cmd/preflight"
	"github.com/keitaroinc/enabler/cmd/util"
	"github.com/spf13/cobra"
	"os"

	"github.com/mitchellh/go-homedir"
	"github.com/spf13/viper"

	"github.com/keitaroinc/enabler/cmd/setup"
)

var cfgFile, kubeCtx string

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "enabler",
	Short: "A brief description of your application",
	Long: `A longer description that spans multiple lines and likely contains
examples and usage of using your application. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	// Uncomment the following line if your bare application
	// has an action associated with it:
	//	Run: func(cmd *cobra.Command, args []string) { },
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func init() {
	cobra.OnInitialize(initConfig)

	// Here you will define your flags and configuration settings.
	// Cobra supports persistent flags, which, if defined here,
	// will be global for your application.

	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.config/enabler/enabler.yaml)")
	rootCmd.PersistentFlags().StringVarP(&kubeCtx, "kube-context", "", "keitaro", "The kubernetes context to use (defaults to \"keitaro\")")

	// Cobra also supports local flags, which will only run
	// when this action is called directly.
	// rootCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")

	// initialize and register sub-commands e.g.:
	// MainCmd.AddCommand(sub)
	rootCmd.AddCommand(apps.MainCmd)
	rootCmd.AddCommand(kind.MainCmd)
	rootCmd.AddCommand(setup.MainCmd)
	rootCmd.AddCommand(platform.MainCmd)
	rootCmd.AddCommand(preflight.MainCmd)
}

// initConfig reads in config file and ENV variables if set.
func initConfig() {
	log := util.NewLogger("INFO", nil)
	// Set default versions for all required dependencies
	viper.SetDefault("kubectl", map[string]string{"version": "1.17.3"})
	viper.SetDefault("helm", map[string]string{"version": "3.1.2"})
	viper.SetDefault("istio", map[string]string{"version": "1.5.1"})
	viper.SetDefault("kind", map[string]string{"version": "0.7.0"})
	viper.SetDefault("skaffold", map[string]string{"version": "latest"})

	if cfgFile != "" {
		// Use config file from the flag.
		viper.SetConfigFile(cfgFile)
	} else {
		// Find home directory.
		home, err := homedir.Dir()
		if err != nil {
			log.Fatal(err)
			os.Exit(1)
		}

		// Search config in home directory with name ".enabler" (without extension).
		viper.AddConfigPath(home + "/.config/enabler")
		viper.SetConfigName("enabler") // name of config file (without extension)
		viper.SetConfigType("yaml")    // REQUIRED if the config file does not have the extension in the name
	}

	viper.AutomaticEnv() // read in environment variables that match

	// If a config file is found, read it in.
	if err := viper.ReadInConfig(); err == nil {
		log.Infof("Using config file: %s", viper.ConfigFileUsed())
	}

	// Check if something is missing
	viper.AllKeys()

}
