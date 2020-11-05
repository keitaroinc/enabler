package setup

import (
	"fmt"
	"github.com/keitaroinc/enabler/cmd/util"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"os"
	"path/filepath"
	"runtime"
)

var initCmd = &cobra.Command{
	Use:   "init",
	Short: "Initialize infrastructure services",
	Long:  `You can use the init command to download and install all serv ices such as: kind, kubectl, istioctl, helm and skaffold`,
	Run: func(cmd *cobra.Command, args []string) {
		log := util.NewLogger("INFO", nil)
		// create dirs
		path, err := os.Getwd()
		if err != nil {
			log.Error(err)
		}
		binPath := filepath.Join(path, "bin")
		if _, err := os.Stat(binPath); os.IsNotExist(err) {
			os.Mkdir(binPath, 0755)
		}

		// kubectl
		name := "kubectl"
		dep := viper.GetStringMapString(name)
		url := fmt.Sprintf("https://storage.googleapis.com/kubernetes-release/release/v%s/bin/%s/amd64/kubectl", dep["version"], runtime.GOOS)
		err = InstallDependency(name, url, filepath.Join(binPath, name))
		if err != nil {
			// do something
		}

		// helm
		name = "helm"
		dep = viper.GetStringMapString(name)
		url = fmt.Sprintf("https://get.helm.sh/helm-v%s-%s-amd64.tar.gz", dep["version"], runtime.GOOS)
		err = InstallDependency(name, url, filepath.Join(binPath, name))
		if err != nil {
			// do something
		}

		// istio
		name = "istio"
		dep = viper.GetStringMapString(name)
		if runtime.GOOS == "linux" {
			url = fmt.Sprintf("https://github.com/istio/istio/releases/download/%s/istioctl-%s-%s.tar.gz", dep["version"], dep["version"], runtime.GOOS)
		} else if runtime.GOOS == "darwin" {
			url = fmt.Sprintf("https://github.com/istio/istio/releases/download/%s/istioctl-%s-osx.tar.gz", dep["version"], dep["version"])
		}
		err = InstallDependency(name, url, filepath.Join(binPath, name))
		if err != nil {
			// do something
		}

		// kind
		name = "kind"
		dep = viper.GetStringMapString(name)
		url = fmt.Sprintf("https://github.com/kubernetes-sigs/kind/releases/download/v%s/kind-%s-amd64", dep["version"], runtime.GOOS)
		err = InstallDependency(name, url, filepath.Join(binPath, name))
		if err != nil {
			// do something
		}

		// skaffold
		name = "skaffold"
		dep = viper.GetStringMapString(name)
		url = fmt.Sprintf("https://storage.googleapis.com/skaffold/releases/latest/skaffold-%s-amd64", runtime.GOOS)
		err = InstallDependency(name, url, filepath.Join(binPath, name))
		if err != nil {
			// do something
		}

		log.Infof("IMPORTANT: Please add the path to your user profile to %s directory at the beginning of your path", binPath)
		log.Infof("$ echo export PATH=%s:$PATH >> ~/.profile", binPath)
	},
}
