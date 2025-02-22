package tech.followthemoney.meta;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Dataset {
    private final static Logger log = LoggerFactory.getLogger(Dataset.class);

    private final Catalog catalog;
    private final String name;
    private List<String> children;
    private String label;

    public Dataset(Catalog catalog, String name, String label) {
        this.catalog = catalog;
        this.name = name.intern();
        this.label = label;
        this.children = new ArrayList<>();
    }

    public String getName() {
        return name;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }
    public boolean isCollection() {
        return !children.isEmpty();
    }

    public List<Dataset> getChildren() {
        List<Dataset> datasets = new ArrayList<>();
        for (String child : children) {
            Optional<Dataset> dataset = catalog.getDataset(child);
            if (dataset.isPresent()) {
                datasets.add(dataset.get());
            } else {
                log.warn("Missing child dataset (of {}): {}", name, child);
            }
        }
        return datasets;
    }

    public void setChildren(List<String> children) {
        this.children = children;
    }

    public List<Dataset> getDatasets() {
        List<Dataset> datasets = new ArrayList<>();
        datasets.add(this);
        for (Dataset child : getChildren()) {
            datasets.addAll(child.getDatasets());
        }
        return datasets;
    }
}
